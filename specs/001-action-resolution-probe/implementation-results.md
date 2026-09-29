# Implementation Results: Action Resolution Probe (Real, Automated Run)

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Tasks**: [tasks.md](tasks.md)
**Date**: 2026-09-29
**Method**: Real code (`src/`), real tool-calling, real externalized state, run against the
live Gemini API (`gemini-3.8-flash`), with an automated LLM-judge check replacing the human
reviewer probe-results.md relied on. No relay, no human in the loop during execution.

## Headline result

**SC-002 came back at 0 contradictions** across 8 resolved, real-tool-calling turns — the
actual measurement this feature was built to produce automatically, which probe-results.md
could only estimate by hand. This is the first genuine evidence (not just a favorable-conditions
anecdote) that Patterns P8 and P13's core mechanism holds up outside a relayed chat.

## Success Criteria results (per spec.md), this run

| # | Criterion | Result |
|---|---|---|
| SC-001 | 100% of resolved actions produce a computed degree | **True.** 8/8 resolved turns had a `roll_check` call and a populated degree. |
| SC-002 | Rate of narration/degree contradiction (target 0) | **0/8**, per an independent LLM-judge call (fresh context, no prior conversation bias) — see limitations below. |
| SC-003 | State changes traceable from the log alone | **Yes.** State changed on exactly turns 4, 7, 9 — a failed persuade attempt, a failed reckless attack flurry, and pushing through pain while fleeing. All three are turns where the narration implies harm; none of the 5 other resolved turns (including 2 successes that logically shouldn't cost anything) changed state incorrectly. |
| SC-004 | Stakes-free turns correctly skip `roll_check` | **True.** Both intentionally stakes-free lines ("I look around and ask what's going on here," "I take a slow breath and steady my nerves") were classified `requires_resolution=false` and never called `roll_check`. |

Full tally: **10 turns total, 8 resolved (4 Success, 4 Failure, 0 Critical Success, 0 Critical
Failure), 2 stakes-free.**

## Comparison to probe-results.md (the earlier relayed-chat session)

| | Relayed-chat probe (13 turns) | This run (10 turns) |
|---|---|---|
| Mechanism tested | Model reasoning about degrees, self-graded, human-relayed | Real tool-calling, real state file, automated judge |
| SC-002 (contradictions) | 0, but **self-reported** — the model graded its own session and missed a real issue (an unearned pronoun) | 0, via an **independent** judge call with no access to the narrating turn's own context |
| Degree distribution | 5 Success, 5 Failure | 4 Success, 4 Failure |
| Real risk this exercised | None — no real tool call existed to skip or misuse | The actual risk this feature was scoped to test: does the model call the right tool, with the right arguments, every time, when driven for real |
| DM-craft issues found | Yes — a pacing soft-lock (turns 6-8), a compound-question granularity gap | None observed this run, but this script didn't specifically probe for them (different test, not evidence they're solved) |

**What this confirms**: the earlier probe's mechanical-consistency finding was not just an
artifact of favorable, self-graded conditions — an independent check, on a real tool-calling
architecture, still finds 0 contradictions.

**What this does NOT confirm**: this is still one run, one script, one model
(`gemini-3.8-flash`), and the judge itself is a single bounded LLM call, not a proven-reliable
classifier (see Limitations). Pattern P13's harder claim — that this holds up unattended, at
scale, over long sessions — remains genuinely untested beyond this scope.

## Real engineering findings from actually building this (not just the mechanic)

These came from the build itself, not from the resolution mechanic, and are worth recording
because they'd bite anyone repeating this work:

1. **`gemini-2.5-flash` is deprecated for new users.** The API's own error message pointed at
   `gemini-3.8-flash` and mentioned a newer "Interactions API" — confirming a web search result
   flagged earlier as unverifiable was, in fact, accurate, just about a different surface than
   assumed.
2. **`google-genai`'s own README example uses `role='tool'` for function responses, but the
   live API rejects it** ("Role 'tool' is not supported"). `role='user'` is what actually
   works — matching Anthropic's equivalent convention. Documentation examples are not
   guaranteed current; verify against the live error message when in doubt.
3. **`FunctionDeclaration` uses `parameters_json_schema`, not `parameters`** — caught by
   checking the SDK's GitHub README directly rather than trusting the first search result.

None of these are design/mechanic findings — they're exactly the kind of "cheap to reverse"
plumbing issue research.md's provider-swap decision anticipated, and all three were fixed by
touching only `src/dm_agent.py`, confirming that design held.

## Limitations (read before treating SC-002=0 as a settled result)

- **The judge is one bounded LLM call, not a validated classifier.** It could itself be wrong,
  and the constitution's own Pattern P13 note about self-judging bias is relevant even though
  this judge call uses fresh context — it is still the same provider/model family as the
  narrating turn. A truly independent judge (a different model family, per Pattern P13's
  documented requirement for the *game's own* eventual gate) was not used here, since this is
  test tooling, not the live game's architecture.
- **One run.** No repeated trials, no variance measurement, no adversarial script targeting the
  judge's own blind spots.
- **This script's actions were all reasonably well-formed.** It did not specifically stress-test
  the DM-craft gaps (soft-locks, compound-question granularity) the way the earlier relayed
  session's live, human-driven play did — a clean result here says nothing about whether those
  specific gaps are fixed.

## Recommended follow-ups

1. Run this script multiple times to get an actual variance estimate on SC-002, not a single
   data point.
2. If a real judge-gate is ever built into the live game (Principle III's revisit trigger), do
   not reuse this test harness's judge call as-is — it doesn't meet Pattern P13's
   independent-model-family requirement.
3. Consider a second scripted run specifically targeting the DM-craft gaps found in
   probe-results.md (an intentionally inconclusive investigation sequence, a fresh compound
   question under the graduated-reveal rule) to see if those hold up under real tool-calling too.
