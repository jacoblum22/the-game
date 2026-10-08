# Implementation Plan: Adjudication

**Branch**: `worktree-agent-a17c5ae17c441856e` (spec `007-adjudication`) | **Date**: 2026-10-08 |
**Spec**: [spec.md](spec.md)

## Summary

Move the gate, necessity and difficulty decisions from the Reader and Framer to code, per the R2-C rules. The
Reader shrinks to verb, target, three facets, shape and question kind; `check_gate` becomes a pure function; a
new `necessity` module decides the no-roll classes; the Framer picks an obstacle class plus a bounded nudge;
`frame_check` enforces the snag cap, the critical-failure guard, cost-follows-source and computes "Another way"
alternatives; the OFFER renders from a template; the CLI uses one menu convention. Design decisions:
[research.md](research.md). Types: [data-model.md](data-model.md). Player-facing contract:
[contracts/offer.md](contracts/offer.md).

## Technical Context

**Language/Version**: Python 3.12 (`py -3.12`), Pydantic v2 (existing).
**Primary Dependencies**: none new.
**Storage**: the existing event store; frames and pauses gain optional fields only (old saves load: extras ignored,
new fields defaulted).
**Testing**: pytest (`PYTHONUTF8=1 py -3.12 -m pytest -q -p no:cacheprovider`), ruff, pyright; Reader golden set on
Claude Haiku via the Claude CLI (`evals/playtest.ask_claude`), owner's subscription, no API spend.
**Target Platform**: Windows / any (CLI).
**Project Type**: single project (`engine/`, `play/`, `evals/`, `tests/`).
**Performance Goals**: fewer model calls per turn: no Framer call on certain or plain-reading beats.
**Constraints**: prompt word budgets (`tests/engine/test_prompts.py`) never grow; INV-3 (no numeric schema field:
the nudge is a string enum); lanes (spec 006 owns narration, claims, NPC layer, Narrator/Checker/World schemas).
**Scale/Scope**: ~10 engine modules, 2 prompts, the CLI menu, ~6 test files updated, 3 new test files.

## Constitution Check

- **I (AI-driven resolution; code runs only `[D]` steps)**: the gate class is `[D]` since 00.12.3's R2-C revision;
  necessity's computed parts are 01.4.1's `[D]` computation line; the obstacle class and nudge stay `[J]` with the
  Framer. PASS.
- **III (flexibility within bounds)**: the nudge is bounded to one rung citing a fact. PASS.
- **IV (MVP scope)**: text only. PASS.
- **VI (consolidation)**: this spec retires the stopgaps listed in FR-013 rather than adding beside them. PASS.
- **VII (default-deny capability gate)**: unchanged in kind; the would-be licence is now looked up by code. PASS.

Post-design re-check: no new violations (no new dependency, no new store, deletions outnumber additions in the
Reader and OFFER paths).

## Project Structure

```text
specs/007-adjudication/   plan.md research.md data-model.md quickstart.md contracts/offer.md tasks.md
engine/dm/roles/reader.py, prompts/reader.md      # schema consumer, pre-router, facets → Beat
engine/dm/roles/framer.py, prompts/framer.md      # obstacle class / nudge → ProposedFrame; default frame
engine/dm/schemas.py                              # Reader and Framer sections only
engine/resolve/gate.py                            # pure computed gate (compute_gate + check_gate wrapper)
engine/resolve/necessity.py (new)                 # necessity(), trivial_class(), parties_who_would_act()
engine/resolve/frame.py, costs.py, types.py       # rubric DC, social DC, snag cap, guard, alternatives, menus
engine/resolve/pipeline.py                        # necessity before framing; OFFER block as the pause prompt
engine/dm/oof.py                                  # OFFER template, word maps, glossary
engine/dm/context.py                              # auto_commit default from rules data
engine/llm/offline.py                             # offline Reader/Framer follow the new schemas
play/render.py, play/cli.py                       # one menu convention, `?`
evals/reader_golden.py                            # live Haiku plug, computed gate, negation pairs, odds audit
tests/engine/test_gate_table.py, test_offer_snapshots.py, test_necessity.py (new); existing tests updated
```

## Complexity Tracking

None.
