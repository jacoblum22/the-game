# Implementation Plan: Memory infrastructure (009 part A)

**Branch**: `worktree-agent-abb25593185a07ed6` | **Date**: 2026-10-08 | **Spec**: [spec.md](spec.md)

## Summary

Store primitives for established details (00.6.2, 00.6.6a): the `narrated` certainty, a `persistence` field, a
projection index of details per entity with last use, a computed cap with archiving, a one-value-per-slot writer
and scene-end expiry. Scene cards folded by the projection at `scene_ended` (so a rebuild regenerates them),
`cards_for`, and the recap summary reading them. An alias index and the 12.2.4 spotlight. Per-role projections of
one view selection (`view_for`), used by `build_packet` for every `WorldState` view, plus a Narrator leak test.
"What did I promise X?" answered from commitments. Decisions: [research.md](research.md); shapes:
[data-model.md](data-model.md); entry points for part B: [contracts/api.md](contracts/api.md).

## Technical Context

**Language/Version**: Python 3.12 (`py -3.12`).
**Primary Dependencies**: the engine only (Pydantic).
**Storage**: the event store; details are facts; cards and the details index live in the projection
(`WorldState.details`, `.scene_cards`), rebuilt from events; one new event type `details_used`.
**Testing**: pytest (`tests/engine/test_memory.py` new); replay game re-recorded; `evals/longhorizon.py`.
**Target Platform**: Windows dev machine / cloud sessions, offline.
**Project Type**: library (engine package).
**Performance Goals**: no new model calls; the Narrator view grows ≤ 10% from scene 50 to 300 (aged mode).
**Constraints**: lanes (spec brief): own `engine/store/`, `engine/retrieve/`, `engine/dm/packet.py`,
`engine/world/scenes.py`, `engine/dm/codex.py`, recap (`engine/dm/session.py::recap_summary`). Spec 006 owns
narration, narrator/checker/world roles, claims, mentions; spec 007 owns reader/framer roles, resolve, oof, play.
One small edit in `engine/dm/turn.py` (not a lane file) routes the promise question. No `rules/` edits beyond a
ledger row.
**Scale/Scope**: 300-scene aged store: ~380 entities, ~1,000 facts, 300 cards.

## Constitution Check

| Principle | Effect | Status |
|---|---|---|
| I. AI-driven mechanical resolution | All selection is `[D]` code over the store; no model call added | Pass |
| II. Custom ruleset | Implements R2-E rules as written | Pass |
| III. Bounded flexibility | Details bounded by a closed slot list and a cap | Pass |
| IV. MVP scope | Part A only; narration diff and usage-mark emission deferred to part B | Pass |
| V. Closed primitives | Details are facts; one event type added (`details_used`) for usage marks | Pass |
| VI. Consolidation | Fixes the journal's first-name matching through the alias index | Pass |
| VII. Default-deny gate | Not touched | Pass |
| Technology constraints | No new dependency | Pass |

Post-design re-check: unchanged.

## Project Structure

```text
specs/009-memory/  spec.md plan.md research.md data-model.md quickstart.md contracts/api.md tasks.md
                   implementation-results.md
engine/store/events.py       # FactSet.certainty += narrated; FactSet.persistence; DetailsUsed payload
engine/store/projection.py   # FactRecord.persistence; WorldState.details, .scene_cards; card fold; details_used
engine/store/details.py      # NEW slots(), write_detail(), active_details(), archived_details(), expire_events()
engine/world/scenes.py       # end_scene stages expiry (12.4.8 step 8) before scene_ended
engine/retrieve/scene.py     # recency over stored scene starts; alias index; spotlight(); details in ranking
engine/retrieve/episodes.py  # NEW cards_for(), card_lines()
engine/dm/packet.py          # view_for(role, state, ctx); scene_view(spotlight, cards); build_packet uses view_for
engine/dm/codex.py           # what_you_know via the alias index; promises()
engine/dm/session.py         # recap_summary reads cards
engine/dm/turn.py            # route "what did I promise X?" to promises() (2 lines)
evals/longhorizon.py         # promise probe reads the answer; report unchanged otherwise
tests/engine/test_memory.py  # NEW: writer, cap, expiry, cards, spotlight, views, leak test, promises
```

**Structure Decision**: details helpers sit in `engine/store/` beside clocks and conditions (they return events);
cards retrieval sits in a new `engine/retrieve/episodes.py` because `retrieve/cards.py` means rule cards.

## Complexity Tracking

| Deviation | Why | Simpler alternative rejected |
|---|---|---|
| Edit in `engine/dm/turn.py` | The promise question must be answered out of fiction; turn.py routes OOF answers | Editing `roles/reader.py` (spec 007's lane) |
| New event `details_used` | 00.6.6a item 5: last use is a projection over the log | A fact per use (rule says not a new fact) |
