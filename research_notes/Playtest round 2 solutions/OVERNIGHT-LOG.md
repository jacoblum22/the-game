# Overnight log: round-2 implementation (2026-10-08 into 10-09)

This log tracks the work on branch `milestone-1-playable`. Nothing has been pushed. The plan is in
[00_SYNTHESIS.md](00_SYNTHESIS.md), sections 4 and 5. Each entry below says what landed, how it was checked,
and anything left for the owner.

## Landed

| Commit | What | Gate |
|---|---|---|
| 461b7ad | **B P4 typed renderer** (`engine/text/render.py`). The regex in `fallback.py` is retired. | 1167 passed. 44 of 769 fact shapes now render as empty; all 44 were garbled Oracle slugs. |
| 82c60e5 | **R2-A ranked, budgeted view.** Archived NPC memories no longer leak into it (12.11.7), and the trigger list now heads the view so it can be cached (DL-12-38). | Director cached prefix 25% → 78%; World 83% → 95%. Validator 0/0. |
| fea2397 | **Spec 005 measurement harness:** replay bench, Reader golden set (91 lines, 11 negation pairs), long-horizon harness, baselines. | See baselines below. |
| ad89bba | **R2-A2 cast budget.** Present people are ranked (beat target, then named, then recent interaction, then 12.6.6 weight). Full profiles fit within `view_budget.cast`; the rest go on one capped "also here" line (DL-12-39). | Aged narrator view at scenes 50/200/300: 1337/1612/1952 → **1190/1261/1357**, every section capped. Unit test with 301 people present: 1828/1839/1844. 1177 passed. Validator 0/0. |
| ef269b7 | **R2-B rules wave:** sentence declarations, coverage, per-sentence repair (12.3.1, 12.3.1a, 12.3.3), tier table (12.14.13), default NPC layer (12.11.9), D1/D2/D4/D5 recorded (DL-12-40..44, DL-15-37). New tables `tbl.npc_activity` and `tbl.npc_practice`. | Merge conflicts were only in generated files: re-assembled, anchors recompiled, cards rebuilt. Replay re-recorded because the rule text changed. Validator 0/0. Suite 1176 passed before the re-record. |
| 16b92c2, + | Research notes committed; the model-calls contract updated; `cards.json` rebuilt. | Full suite after merges: 1176 passed, 1 failure (stale `cards.json`, now fixed). Validator 0/0. ruff: the 10 errors in untouched files predate this work. |

## Baselines (spec 005), the gates for later specs

| Measure | Baseline | Gate |
|---|---|---|
| First-draft pass rate | 1.3% | > 50% (spec 006) |
| Turns with cut sentences | 58% | < 15% (spec 006) |
| Narrator calls per turn | 1.81 | ≤ 1.2 (spec 006) |
| Undeclared new elements per draft | 2.88 | < 0.3 (spec 009 diff audit) |
| Reader verb / gate accuracy (golden set; Haiku answers recorded before the round-1 fixes) | 72% / 64% | ≥ 95% / ≥ 98% (spec 007) |
| Recall coverage / promise recall (aged harness) | 0.67 / 0.00 | rises (specs 008, 009) |

## Findings during the night

- **The view still grew 46% over 300 aged scenes after R2-A.** NPCs positioned at the scene's place render
  as full profile blocks with no budget, so a home inn that gathers residents bloats every packet. A fixer was
  dispatched (R2-A2: a budget for people present, plus a compact "also here" line).
- **From the spec 005 agent, routed to later specs:**
  - name generation runs out after about 220 scripted lines (`_seed_lib.py`), for spec 008;
  - the journal matches people by first or last name alone, for spec 009;
  - "what did I promise X?" is not answered from stored commitments, for spec 008 or 009.

## Assumed decisions (owner to confirm)

D5–D8 took their recommended defaults (see 00_SYNTHESIS §4). D9 (a real-Gemini run) and the Laya spike are
deferred to the owner.

## In flight

- R2-C rules wave (adjudication, difficulty rubric + seeded sim, D3/D6/D7).
- Spec 006 (narration contract + NPC layer), started from ef269b7. Model-quality gates run on at most 80
  recorded packets with Haiku via the Claude CLI (subscription, no API spend).
