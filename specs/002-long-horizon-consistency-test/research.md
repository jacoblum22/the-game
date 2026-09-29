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
