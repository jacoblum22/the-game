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
| 91fc837 | **R2-C rules wave:** computed gate (00.12.3 `[D]`), rubric with obstacle classes plus guardrails (00.3.8, 01.6.5, 01.6.8, the new 01.6.13 critical-failure guard), cost follows stakes source (01.6.11, I-155), Safe frames auto-commit (01.7.4), OFFER template plus glossary (12.15.2, 14.2.7). DL-01-29..32, DL-12-50..51. | Ledger merged row by row; derived files regenerated; replay re-recorded. Suite **1177 passed**, validator 0/0. **Sim:** every acceptance target passes except the compound-error bound. When a wrong nudge and a wrong snag hit the same beat, success drops 35 points (target ≤ 25); a single error stays within 25. Nothing was tuned to force a pass. **Owner to decide.** |
| 7f41456 | **R2-E rules wave:** established details (00.6.6a), detail diff on reuse (PR-00-7), scene cards (12.4.8), recap from cards (12.5.3), spotlight and per-role views (12.2.4), diff-mode audit with a skip gate (12.3.1), freshness from usage marks (12.14.11). DL-12-70..76; OEQ-12-20..23. | Suite 1177 passed, validator 0/0. Note: with one value per slot, a person has exactly 8 lasting slots, so the cap of 8 never binds (flagged in DL-12-70 for the owner). |
| 1de755a | **R2-D rules wave:** answer ladder (new 12.10.8 / PR-12-10), `cast` domain (00.11.1), proposal form (00.12.7), reduced case (PR-15-6, 15.9.4), seed packs (12.16.*), I-149 local names. DL-12-60..64, DL-15-38..39. | **Answer-ladder sim:** "I don't know + lead" is 31.6% of ordinary asks at a 50% on-trade mix (target < 35%), but **36.5% at a 30% mix**. No empty success; asking twice gives the same answer 100% of the time; the reduced case is answerable within 3 turns in 30/30 (after one added rule). Suite 1177, validator 0/0. |
| 9fc29e0 | **Spec 008 part A:**<br>• seed packs: place looks, furniture and exits; 2–4 knowledge facts and a stance per NPC; document text<br>• casting (the `cast` domain)<br>• reduced case builder (`engine/gen/case.py`), with the placement audit moved to M1<br>• I-149 local names<br>• `bind_incident` / `SUBJECTS` retired<br>• name exhaustion fixed | Suite **1197 passed**. Matches the reference seed code on 10 seeds. 30/30 incident cases valid. Scripted long-horizon run of 320 lines: 0 errors (was 7). Narrator packet +107 tokens (+0.7%). |
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

- Spec 007 (adjudication), started from 91fc837. The gate is the Reader golden set, scored with Haiku via the
  Claude CLI.
- Spec 008 part B (the answer ladder) waits for specs 006 and 007.
- Spec 009 part A (store detail primitives, scene cards, spotlight, per-role views, leak test, promise recall,
  full-name alias matching), started from 9fc29e0. Part B (the narration-side detail diff and the diff-mode
  Checker) waits for 006.
- Spec 006 (narration contract + NPC layer), started from ef269b7. Model-quality gates run on at most 80
  recorded packets with Haiku via the Claude CLI (subscription, no API spend).
