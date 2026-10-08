# Implementation Plan: Narration contract and default NPC layer

**Branch**: `worktree-agent-a8fed8017034eb06e` | **Date**: 2026-10-08 | **Spec**: [spec.md](spec.md)

## Summary

The Narrator returns declared sentences (B P1); code judges them (refs resolved into subject-given claims for
`check_claims`, deterministic scans, coverage of must-name record items), routes new elements by tier (C P1,
B P5), and repairs one sentence at a time (B P3). A deterministic NPC layer (C P4, 12.11.9) writes every
present NPC's activity and every engaged NPC's response into the record as handle-bearing lines, replacing
the World call on the default path. The Checker stays as an audit (spec 009 makes it diff-mode).

## Technical Context

**Language/Version**: Python 3.12 (engine targets 3.11+), Pydantic v2
**Primary Dependencies**: none new (stdlib + existing engine modules)
**Storage**: the event store (facts for activities, T1a details, T1b answers; meta for the scene's "spoken
with" list)
**Testing**: pytest (`tests/engine/`, `tests/evals/`), replay fixtures (`tests/replay/games`, re-recorded),
`evals/longhorizon.py --mode scripted`, `evals/replay_bench.py` with plugs
**Target Platform**: Windows/Linux CLI
**Project Type**: game engine library + CLI
**Performance Goals**: narrator calls per turn ≤ 1.2; no added model call on the default path
**Constraints**: prompt word budgets (`tests/engine/test_prompts.py`, narrator 1000); INV-3 (no numeric schema
fields: sentence indices are string enums); Gemini schema subset (enums ≤ the converter's limits); lanes (007
owns Reader/Framer/gate/oof; 008/009 own Talk regexes, incident, diff Checker)
**Scale/Scope**: ~6 engine modules touched, 2 new (`engine/dm/handles.py`, `engine/dm/npc_layer.py`), 1 new
audit module (`engine/audit/declare.py`), 1 eval plug (`evals/narration_plug.py`)

## Constitution Check

| Principle | Effect | Status |
|---|---|---|
| I. AI-driven resolution | The narrator still makes every narration judgment (declarations are its `[J:enum]`, 12.3.1); code runs only `[D]` steps (12.3.1a scans, 12.3.2 verdicts, 12.11.9). The want/refusal match is `[J:flag]` (12.2.9): code only pre-filters candidates by word overlap; any candidate goes to the World call when enabled (research R6) | Pass |
| II. Custom ruleset | Implements R2-B rules; no rules edits | Pass |
| III. Bounded flexibility | T1a write-as-narrated is ruled (DL-12-40), not narrator override | Pass |
| IV. MVP scope | Single-player text | Pass |
| V. Closed primitives | `element_kind` is a closed list from rules data | Pass |
| VI. Consolidation | Retires 12 stopgaps (tasks phase "Retire") | Pass |
| VII. Default-deny gate | Untouched (spec 007) | Pass |
| Technology | No Gemini spend; Claude CLI (Haiku, subscription) only for the eval plug | Pass |

Post-design re-check: unchanged.

## Project Structure

```text
specs/006-narration-contract/  plan.md research.md data-model.md quickstart.md contracts/narrator.md tasks.md
engine/dm/handles.py        # NEW: record items with handles (R1…), must_name, words, rendered line
engine/dm/npc_layer.py      # NEW: 12.11.9 activity, practice, response, voiced refusal
engine/audit/declare.py     # NEW: declared sentences, tier lookup, scans, coverage, ref→claim
engine/audit/claims.py      # undetermined split by tier; retire _FORBIDDEN_NEW/_DEEDS/GIVEN_NOTES/... ; cited sources
engine/audit/fallback.py    # plain fallback = render every must-name item (from handles)
engine/dm/narration.py      # per-sentence judge + repair loop; retire _carry/_mention_name/pure_cut/...
engine/dm/roles/narrator.py # record_text with handles; sentences schema; repair message
engine/dm/roles/checker.py  # check given sentences (indices kept)
engine/dm/roles/world.py    # tie-breaker over candidate motives only
engine/dm/world_step.py     # npcs_respond → npc_layer (Talk regexes untouched)
engine/dm/schemas.py        # narrator (sentences | fiction-fallback) and repair schemas
engine/dm/roles/prompts/narrator.md, world.md
engine/llm/offline.py       # offline narrator speaks the new schema
evals/narration_plug.py     # replay plugs: packet→new packet, Claude CLI narrator, packet judge, repair sim
```

## Phases

- **0 Research**: [research.md](research.md) (decisions R1–R10).
- **1 Design**: [data-model.md](data-model.md), [contracts/narrator.md](contracts/narrator.md),
  [quickstart.md](quickstart.md).
- **2 Tasks**: tasks.md (speckit-tasks).
