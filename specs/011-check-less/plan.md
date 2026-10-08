# Plan: Check less (spec 011)

**Spec**: [spec.md](spec.md). **Tasks**: [tasks.md](tasks.md). Scope: R2-G "engine checklist → Spec 011" items 1–12.

## Technical context

Python 3.12, Pydantic, SQLite event store; tests pytest; models behind `engine.llm` (offline, Claude CLI, Gemini).
Lanes: this spec owns `engine/dm/narration.py`, `engine/audit/` (claims, declare), `engine/dm/roles/{narrator,
checker,framer}.py`, `engine/dm/mentions.py`, `engine/dm/npc_layer.py`, `engine/store/details.py`,
`engine/resolve/`, prompts and schemas. Spec 012 owns dispute, CLI, Reader dispute classification, `pinned`.

## Constitution check

I (code resolves, model narrates): kept, blocking verdicts and NPC responses stay code. IV (MVP discipline):
deletions over additions (the per-turn audit, `_apply_writes`, `_settle`, the skip gate, the detail cap go).
VII (default-deny): the blocking list is closed data. No violation.

## Design (by checklist item)

1. **Retire keys.** `pacing.yaml`: drop `details.max_active`, `claim_check.audit.skip_enabled`.
   `details.active_details` = scene details + every lasting one ordered by salience (2: seeded, generated, a
   correction) then last use; `archived_details` and `max_active` go. `narration.audit_mode(ctx)` → `sampled`
   when `crc32(turn_id) % full_extraction_every == 0`, else `off`.
2. **Speech.** `DeclaredSentence.speaker` (schema enum: present people, never the PC; `none` first).
   `declare.voices(s) -> (narration, speech spans)`: quoted spans are speech when a speaker is declared; a speaker
   with no quotes makes the sentence reported speech. Code scans read the narration only (mechanics read all).
   Speech checks: speaker present and not the PC; a quote attributed to "you" (no speaker) must be covered by the
   player's message, else `pc_agency` (cut). Delivered speech → `said` records on the turn record; a stored
   unknown name heard in speech → `social.learn_name(..., "heard")`.
3. **Claim log.** `NarrationResult.claim_log` → `TurnRecord.claim_log` `{turn, sentence, class, verdict,
   store_value}` (+ `blocking_miss` on sampled entries). Per-turn code logs: pronoun clashes, detail clashes,
   undeclared sentences, unwritable new elements, speech without a speaker.
4. **Certain subject.** `claims.certain(state, subject, text, pc, scope)`; `check_claims(..., texts=)` returns
   `no_verdict` for an uncertain subject in either direction. `claims.blocking(c, v, rules)` reads
   `pacing.yaml#claim_check.blocking` (possession: relevant items only; identity: names only).
5. **Code scans** (`scan_sentence`, `_polarity`): numerals, unknown names, sealed strings, outcome words against
   cited beats (an undeclared sentence: against the turn's only rolled beat). Nothing else fails a sentence.
6. **T2.** `tier_of`: unknown kind → T1a. T2 cut only in narrator voice; a T2/T1b element named only inside
   speech is testimony (logged, not written).
7. **Clashes.** `profile_diff` contradictions log; only blocking slots (held weapon; held/pinned/restrained/
   mounted posture) redraft. A T1a element that cannot be written is logged, not cut.
8. **Unsourced change / sweep.** With the per-turn audit gone, `unsourced_change` only reaches the sampled log.
   The scene-end sweep has no engine code; nothing to change.
9. **I-159.** `frame._levers`: on a tier obstacle with a nonzero nudge or class `other`, every cited Precision snag
   applies as Protective (stakes +1 each, clamped), with a note.
10. **I-160(a).** Framer field `reach_two_factors` (bool): `pipeline._frame` routes to G4 (`missing_kind
    zero_reach`, 01.3.7 redirect, a `g4` ruling) before the OFFER; nothing spent.
11. **I-176.** `Beat.pressure` (from the Reader's mark); Framer `asks` enum on a Talk request
    (`social.yaml#event_tags.asks`, else `none`) → `Frame.asks`. `npc_layer.event_tags` derives tags; refusals by
    kind, wants by object (text suffix) through `event_tags.refusals/.wants`; rows served 9/8, defeated 2 (1 at
    Hostile), engaged 6, then the clamp. World call only when no tag matches and the NPC holds a want and a
    refusal. Crowd: with practice `crowd` and nobody engaged, one `tbl.npc_action` row clamped to the crowd rows →
    scene fact `crowd_response` on the place + an `NpcActionEntry` record line.
12. **Metrics.** `evals/longhorizon.py::narration_loop` adds claim-log entries per 100 narrated turns by class and
    sampled blocking-list misses per 100 turns (and per sampled turn).

## Research decisions

- **Claim log on the turn record**, not events: no projection change, spec 012 reads it per turn. Alternative
  (an event type) touches `events.py` (012's lane).
- **Said records on the turn record** for the same reason; ceiling: no per-speaker index (add one when the Oracle
  settles a said claim the player acts on).
- **World fallback reading** (item 11): literal; the long-horizon run reports how often it fires.

## Touched outside the lane

`engine/store/records.py` (two TurnRecord fields), `engine/dm/roles/reader.py` (carry `pressure` into `Beat`),
`engine/llm/offline.py` (new schema fields), `rules/data/pacing.yaml` (two retired keys).
