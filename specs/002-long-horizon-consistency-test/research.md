# Phase 0 Research: Long-Horizon Consistency Stress Test

Technical Context left no `NEEDS CLARIFICATION` markers. This phase records the rationale
behind each design decision, most of which trace directly to
[reports/Long horizon LLM narrative benchmarks.md](../../reports/Long%20horizon%20LLM%20narrative%20benchmarks.md).

## Decision: adapt NCP-Bench's three-stage pipeline structure, not invent a new one

**Rationale**: NCP-Bench's own construction pipeline (trajectory → commitments → initial
facts, each stage conditioned on the prior one, with prompt templates published MIT-licensed)
is the field's actual standard for synthetic long-horizon scenario construction, not a
shortcut relative to real playthroughs. Reinventing this structure from scratch would discard
a proven design and its most important discipline: the T=0 Absolute Isolation Principle
(positively asserting ignorance of not-yet-true facts, not merely omitting them), which is
what makes a synthetic seed trustworthy rather than a hand-wave.

**Alternatives considered**: writing a single freehand "story so far" prose recap and
hand-extracting state from it (rejected: no isolation discipline, easy to accidentally leak
future knowledge into the seed, which would invalidate everything measured afterward); using
a completely different construction method (rejected: no other published, reusable method was
found in the research that matches our exact tool-calling architecture).

## Decision: original campaign outlines, not adapted copyrighted synopses

**Rationale**: NCP-Bench uses movie synopses as source material; we use short, original
outlines we write ourselves. We're borrowing the extraction *method*, not the specific source
material — nothing about the pipeline's value depends on the input being a real movie.

## Decision: generic multi-category `WorldState`, not a fixed schema per campaign

**Rationale**: research is specific about which fact categories fail first — facts that
*change over time* (numeric resources, possession, position, status/existence flags) are
categorically more fragile than static lore, ahead of any particular narrative content. Rather
than hardcode one campaign's specific facts into the state schema, `WorldState` uses generic,
typed containers (a resources dict, a possessions dict, a position field, a status-flags dict)
that the extraction pipeline populates per-campaign. This keeps the schema reusable across the
3+ scenarios SC-001 requires, while still guaranteeing every scenario exercises the categories
research says matter most.

**Alternatives considered**: a fully freeform JSON blob with no typed categories (rejected:
would make FR-006's category-attribution requirement impossible to implement cleanly); a fixed
schema hardcoded to one specific campaign (rejected: doesn't generalize to SC-001's requirement
of 3+ distinct scenarios).

## Decision: conflict auditor extends `judge_consistency`, is not a new architecture

**Rationale**: the single largest quantified mitigation found anywhere in the research (a
64.78% reduction in critical hallucinations) is architecturally a second-pass LLM call checking
narration against an explicit fact/knowledge store before it's accepted — which is exactly what
Feature 001's `judge_consistency` already does at small scale (checking narration against one
computed degree). Extending it to check against a fact ledger and commitment set, and to
classify the conflict type/category, is a natural generalization, not a new mechanism. Building
a genuinely independent-model-family judge (per Pattern P13's eventual requirement) is
explicitly out of scope here, per spec.md's Assumptions — this auditor still shares a model
family with the narrator, a known, accepted limitation carried forward from Feature 001.

**Alternatives considered**: hierarchical/summarization-based memory (HiAgent-style) as the
primary mitigation (rejected for this feature: the one benchmarked instance of this approach
cut commitment conflicts sharply but nearly tripled player-input conflicts, an unresolved
tradeoff its own authors call open — not something to adopt as a default before even measuring
our own baseline).

## Decision: scripted adversarial + natural player persona, both required

**Rationale**: research found persona condition changes commitment-conflict rate substantially
(roughly 3x) but barely moves fact-conflict rate (56% vs. 60% in NCP-Bench's data) — meaning
fact-tracking failure is driven mostly by accumulated turn count itself, not adversarial
pressure. Running both conditions lets Feature 002 check whether our own architecture shows the
same pattern, which is itself a useful, comparable finding, not just flavor.

## Decision: turn cap sequencing — validate small before scaling to the spec's full target

**Rationale**: spec.md sets a provisional 50-turn cap and SC-002's 5-run target, but research
shows most models' failures cluster well before turn 20-30. Attempting the full 5×50 batch
before the pipeline itself is proven working would risk spending significant real API cost on
a broken harness. Development sequencing (not a spec change): validate scenario generation +
one short run (~15-20 turns) end-to-end first, confirm the auditor and category-attribution
logic work correctly on that small case, then scale up to the full SC-002 target.

## Decision: JSON-schema validation of pipeline output is the only new unit-testable surface

**Rationale**: consistent with Feature 001's split (pure math unit-tested, live-API behavior
scripted), the only genuinely deterministic new logic is structural validation of the
pipeline's three extraction outputs — do commitments reference trajectory node IDs that
actually exist, are IDs unique, are required fields present. The semantic content (is this
trajectory node sensible, does this commitment actually reflect the outline) is not
deterministically checkable and isn't unit-tested; it's exercised live via the scripted harness.

**Output**: All Technical Context items resolved above; no remaining `NEEDS CLARIFICATION`.

## Amendment (post-T021): fast-forward seeding revisits the rejected "freehand recap" alternative

**Context**: this feature's own initial research brief proposed exactly what the "freehand
recap" alternative above rejected — a synthetic "story so far" plus a pre-populated state, to
avoid paying for 80+ real sequential turns to reach a long-session state. What actually got
built for T021 played every turn live from `sequence_index 0` instead, at real cost roughly
proportional to the full turn count. After T021 (which needed several corrective iterations
before its numbers were trustworthy — see `implementation-results.md`), the project owner asked
why a synthetic recap wasn't used, given the whole session's trajectory and commitments are
already generated ahead of time.

**Resolution**: re-reading the original rejection shows it was about the *lack of isolation
discipline* in a freehand recap — "hand-extracting state from it," with no independent check
that it doesn't leak future knowledge — not about the fast-forward concept itself. The existing
pipeline's isolation discipline (Decision 1, above) generalizes cleanly to an arbitrary cutoff
point instead of always `sequence_index 0`: `extract_state_at_cutoff` and `check_isolation` both
take a `cutoff_index` now (default `-1`, the original t=0 behavior, so no existing caller
changes). See `contracts/pipeline-prompts.md` §7 for the full contract. This is not a reversal of
the original decision's reasoning, only a correction of scope: the rejected alternative and this
addition are different things that happened to use the word "recap."

**Second correction, before this ever ran a real batch**: the first implementation of the above
generated a short (3-6 sentence) prose recap and injected it into the DM's system prompt. Caught
in review before any live session used it: a short summary doesn't test what "long-horizon
consistency" is actually about. NCP-Bench-style degradation is about whether a genuinely *large
volume* of accumulated turn content in the model's context causes attention/recall problems — a
five-sentence briefing has essentially none of that volume, no matter how accurate it is.
Testing against a recap measures "can the DM correctly continue given an accurate summary," a
real but much narrower and easier question than the one this feature exists to ask.

**Final design**: `generate_synthetic_transcript` produces a full alternating
`(player_action, dm_narration)` transcript, granular enough to total a real target turn count
(not one turn per plot beat — ordinary investigative/conversational turns between beats too),
generated in chunks rather than one shot. `check_transcript` verifies it holistically before
trust: isolation, internal self-consistency, agreement with the independently-computed cutoff
state, and commitment compliance. The harness splices this transcript directly into the real
conversation history as literal prior turns, so the model contends with actual bulk context
instead of a compressed stand-in for it.

**Known limitation of this design, stated honestly**: the synthetic transcript is authored
together, in one or a few generation passes, not turn-by-turn independently the way a real
session unfolds — the model can effectively "see" the whole thing at once while writing it. This
likely makes it *more* internally consistent than an organically-generated turn-by-turn history
would be. If real turns run on top of this transcript show few conflicts, that is a genuinely
weaker result than the same finding from a fully live session would be — a much better proxy for
"does bulk context cause degradation" than a recap, but not a perfect substitute for actually
playing out every turn.
