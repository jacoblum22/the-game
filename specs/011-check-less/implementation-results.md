# Implementation results: Check less (spec 011)

Scope: R2-G "engine checklist → Spec 011", items 1–12 (`rules/_process/reports/R2-G-report.md`). Baselines:
`evals/baselines/live_narration_011.txt` (live), `evals/baselines/longhorizon_011.txt` (offline).

## Gates

| Gate | Result |
|---|---|
| Full suite | **1669 passed**, 4 skipped (1657 before; replay re-recorded: packets changed on purpose) |
| ruff (repo) / pyright (touched files) | clean / clean except one pre-existing error in `pipeline._contact` (line 350, untouched) |
| Rules validator | 0 ERROR / 0 WARN (cards recompiled; unchanged) |
| Offline scripted, 300 lines | **0 engine errors**; first draft 86.4% (86.1% at 010), cut turns 13.6%, 1.27 calls/turn |

## Live (Haiku via the Claude CLI; seed 7, 16 lines → **19 narrated turns**, budget 25; no API spend)

| Gate | Spec 010 live | **Spec 011 live** | Target |
|---|---|---|---|
| First draft delivered as drafted | 42.1% (8/19) | **94.7% (18/19)** | > 50%, met |
| Turns with a cut, rendered line or fallback | 26.3% (5/19) | **0.0% (0/19)** | < 15%, met |
| Narrator calls per narrated turn | 1.37 | **1.05** | ≤ 1.2, met |
| Engine errors | 0 | 0 | 0 |

- **Claim log per 100 narrated turns: 147.4** — position/supported 63.2, knowledge/supported 15.8,
  location_time/testimony 10.5, attitude/supported 10.5, identity/logged 5.3, action/supported 5.3,
  knowledge/no_verdict 5.3, speech/no_speaker 5.3, knowledge/testimony 5.3, existence/supported 5.3,
  identity/undetermined 5.3, location_time/supported 5.3, new_element/undeclared 5.3.
- **Sampled audit:** 4 of 19 turns sampled; **blocking-list misses 0** (0.0 per 100 turns). The sample is small:
  a miss rate under about 5 per 100 cannot be ruled out yet (OEQ-12-23 needs a longer run).
- The one repaired turn: a declared knowledge element (T1b) the Oracle settled "no".
- The narrator declared `speaker` on 6 of 156 sentences; 6 said records were kept. Treat every figure as ±10 points.

## What was built (by item)

1. `details.max_active` and `claim_check.audit.skip_enabled` removed from `pacing.yaml` with their readers
   (`details.max_active`, `archived_details`, the `_lasting` slice; `narration.audit_mode` is `sampled`/`off`).
   A correction (`source: correction`) has salience 2.
2. Narrator schema `speaker`; `declare.voices` / `pc_quotes`; speech checks; `said` records on `TurnRecord.said`;
   a stored unknown name heard in speech is learned (`how: heard`).
3. Blocking list (`claims.blocking`); the claim log (`TurnRecord.claim_log`).
4. Certain subject (`claims.certain`, `check_claims(texts=)` → `Verdict.uncertain`, logged `no_verdict`).
5. Code scans every turn on the narrator's voice; outcome words against cited beats (an uncited sentence: the only
   rolled beat).
6. Uncertain kind T1a; T2 cut only in the narrator's voice; in speech it is testimony.
7. Detail clashes logged unless the slot blocks (held weapon, coarse posture); an unwritable T1a logged.
8. The per-turn audit is gone, so `unsourced_change` only reaches the sampled log.
9. I-159 in `frame._levers`. 10. I-160(a): `reach_two_factors` → `gate.zero_reach` G4 before the OFFER.
11. I-176: `npc_layer.event_tags`, `motive_tags`, `want_row`; World fallback; `crowd_response`.
12. `evals/longhorizon.py`: claim log by class, sampled misses per 100.

**Retired:** `_apply_writes`, `_settle`, `_audit`, `_subject_given`, `_in_lead`, `details.max_active`,
`archived_details`, the skip gate, the per-turn diff audit, pronoun and echoed-quote failures (now logged).

## Touched outside the lane
`engine/store/events.py` (one word: `"heard"` added to the knowledge `how` literal), `engine/store/records.py`
(`claim_log`, `said`), `engine/dm/roles/reader.py` (carries `pressure` into `Beat`), `engine/llm/offline.py`
(new schema fields), `rules/data/pacing.yaml` (two retired keys). `packet.py` not touched.

## Deferred / readings disclosed
- The scene-end sweep (12.4.8 step 4) has no engine code; nothing to restrict.
- Item 11's World fallback reads the checklist literally: no tag matches and the NPC holds both a want and a
  refusal (opposite rows). Tags `names_object`, `asks_truce`, `asks_surrender` never fire yet (no want-object
  entity, no parley beat), and `harms_innocent` reads no record of wrongdoing.
- Said records live on the turn record, not indexed per speaker; settling a said claim the player later acts on
  (12.3.1b item 1) is not built.
- Quoted words with no declared speaker count as speech (logged `no_speaker`), unless attributed to "you".
