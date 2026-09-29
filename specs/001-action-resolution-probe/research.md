# Phase 0 Research: Action Resolution Probe

Technical Context left no `NEEDS CLARIFICATION` markers, so this phase documents the rationale
behind each decision rather than resolving open unknowns.

## Decision: Python 3.11+, direct Anthropic SDK tool-use, no MCP, flat JSON storage

**Rationale**: This feature exists to test one narrow question (does real tool-calling +
externalized state hold up), not to establish the game's production architecture. Every choice
here was picked for being cheap to reverse, not for being permanently correct — consistent
with the project owner's explicit concern about over-committing to complex infrastructure
before it's earned. Python has no ecosystem lock-in for this scope; the official SDK's tool-use
is the most direct way to force a real separation between narration and mechanics; MCP adds
protocol/interoperability machinery this single-process script doesn't need yet; a flat JSON
file is sufficient for one continuous session with no persistence requirement.

**Alternatives considered**: MCP-wrapped tools (rejected: solves a multi-client interoperability
problem this feature doesn't have); a real database (rejected: no persistence requirement
exists to justify it); Node/TypeScript (no strong reason either way — Python was chosen only
because it's marginally faster to script this specific shape of thing, not for a durable
technical reason).

## Decision: model is a runtime-configurable parameter, defaulting to a cost-efficient model

**Rationale**: Nothing about this feature's purpose depends on which specific model is used —
the earlier relayed-chat probe already used Haiku successfully for the same reasoning task at
low cost. Hardcoding a model name would quietly turn a reversible choice into a sticky one; a
config/env-var default keeps swapping models a one-line change, matching the "everything here
is cheap to change" framing in plan.md.

**Alternatives considered**: hardcoding a specific model (rejected: unnecessarily sticky for a
choice nothing here depends on); defaulting to the most capable available model (rejected: no
evidence yet that this task needs more capability than the earlier probe already demonstrated,
and cost-efficiency was an explicit project preference for this kind of test).

## Decision: resolution formula (concrete numbers for Pattern P8)

**Rationale**: Pattern P8 in the constitution recommends a PF2e-style degree-of-success branch
but deliberately deferred exact numbers to `/speckit-plan`. This feature needs concrete numbers
to actually run, so they're fixed here, for this feature only, not as a permanent ruleset
decision:

- Roll: 1d20 + a flat modifier (fixed per test scenario, not yet a real character stat system).
- Total = roll + modifier.
- **Critical Success**: Total ≥ DC + 10, OR the raw d20 roll is a natural 20.
- **Critical Failure**: Total ≤ DC − 10, OR the raw d20 roll is a natural 1.
- **Success**: Total ≥ DC (and not already a Critical Success).
- **Failure**: Total < DC (and not already a Critical Failure).

This exactly matches what the earlier relayed-chat probe already used informally, so this
feature's real implementation is directly comparable to those results rather than introducing
a new variable.

**Alternatives considered**: a different die/threshold scheme (e.g. Fate's ladder, dice-pool
counting) — rejected for this feature specifically because the point is to verify the *already-
tested* formula under real tool-calling, not to test a new one; that comparison is a
reasonable future feature, not this one.

## Decision: two tools exposed to the model — `roll_check` and state read/write

**Rationale**: This is the literal P13 boundary. `roll_check(dc)` returns `{roll, modifier,
total, degree}` computed entirely in `resolution.py`, never by the model. `get_state()` and
`update_state(delta)` read/write the JSON session file, so the model must query current state
rather than assume it from its own conversational memory. Full schemas are in
[contracts/tools.md](contracts/tools.md).

## Decision: system prompt encodes P8, P12, P16, P17, and Principle III's default explicitly

**Rationale**: These are behavioral rules, not infrastructure — they belong in the prompt, not
in code, and should be stated as directly as the instructions given to the earlier relayed-chat
subagent (which is the only evidence so far that a model can follow them). No new invention is
needed here, just porting known-working instructions into the real system prompt.

**Output**: All Technical Context items resolved above; no remaining `NEEDS CLARIFICATION`.
