# Plan 023: one owner per question, the goal flows through, take the time, OFFER wording

## Trace first (round-7 saves, read-only; confirms R7-I3 and R7-H2)
- Fighter turn.11: Reader `fact_questions` on `npc.belie_greenwort` "can read the writing on the delivery list"
  (likely) → Oracle d100 08 → `fact.113 = false`; her `entity_created` (seq 222) holds `lic.lang.letters`, role
  "scribe and teacher of letters"; the OFFER (seq 456) cited the closed door, and the snag line came from fact.113.
- Fighter turn.5: `fact.106` predicate `is_not_alert_to_a_hand_reaching_into_his_coat_pocket_while_h` (cut at 60),
  value False; frame.1 `snags: [fact.106]`; `fact_short` negated it again ("is not not alert").
- Fighter turn.4 (input 19): the Reader's one beat is `verb.talk`, `learn` on `item.delivery_list`, method "read the
  list over his shoulder…"; `reads_writing` gated only `verb.observe`; the Letters REDIRECT came at turn.8.
- Explorer turn.12/13: OFFER seq 626, `verb.observe`, `change none`, Safe, secret, `cost.time` cited to fact.116 (an
  Oracle fact about the house); roll d20 1 → "hidden check made". No clock listens to time or exposure (only faction
  goal clocks). An Unfriendly bystander (Roswen, -2) is present but was not the Framer's stakes source.
- Explorer turn.4/10: `fact.105` (Oracle: Morga "is willing…" = false) beside `fact.106` (Morga agreed); turn.10's
  `persuade_to` rolled (Risky, closed door cited to fact.105) and fact.118 "a smaller part of it (…)" superseded
  fact.106.
- Talker turn.12/13: frame.2 `verb.talk`, `change none`, pressure `offer`, threatened `cost.closed_door` form "he
  turns the round down"; near miss → success at cost paid that form (seq 533).
- Fighter turn.8/9: redirect (seq 444) then OFFER (seq 447): Framer `tier hard` on the whole reading intent, +5
  fallback shift → DC 25, 5%.

## Design (prefer deleting machinery)
| Piece | Where | What |
|---|---|---|
| One owner per question | `dm/turn.py` `not_oracle`, `_fiction_questions` | drop a question about a beat's target or a person here (cast or positioned), the PC's own ability/knowledge, or content (wh-words); ask the rest positive and whole at mirrored odds. Deletes `_KNOWS_Q`, `speech_owns`, the `[:60]` cut |
| Positive Oracle facts | `resolve/oracle.py` `positive`, `MIRROR` | one negation removed, the odds mirrored |
| Never a snag | `resolve/frame.py` `_levers`; `dm/schemas.py` `snag_fact_ids` | refused in `frame_check`; not offered in the schema |
| Plain labels | `dm/oof.py` `fact_short` | subject named, one negation, never "not not" |
| Typed goal | `resolve/change.py` `typed_goal`; `pipeline._start`, `_checked` | a `none` goal gets its verb's plain goal; still `none` and costly → ask (01.2.4) |
| Goal-keyed gates | `gate.reads_writing`, `necessity.certain_talk`, `reader.plans` (`asks`), `frame` (`secret`) | keyed on the goal and the method's words, not the verb |
| 01.9.3 | `frame._costs`, `reverses`; `roll.read_result`; `oof.near_miss_choices` | a reversing price carries no success-at-cost severity; a fitting non-reversing one is named |
| Fallback scope | `pipeline._answer_redirect`; `framer.beat_message` | intent/method/how = the fallback; the Framer sees only that |
| Take the time | `necessity.costly`; `pipeline._checked`, `_no_roll` | computed on the typed frame; `advance_time` ×2; RESULT line; fallback at its reach cap |
| Already agreed | Framer `already_agreed` (schema, prompt); `change.agreed_covers`; `apply_change` adds, never replaces | the 60% overlap deleted |
| OFFER wording | `oof._breakdown`, `_chance_line`, `offer_block`; Framer `reach_limit` replaces `reach_whole`/`reach_one_factor` | no 0 terms, no "practised", Safe says "nothing lost" + failing badly, Limited names its factor |
| Target record | `framer.target_record` in the beat message | the Framer sees the target's role and licences (packet.py is spec 024's) |

Justified touches outside the listed lane: `engine/llm/offline.py` (the offline Framer stub's two retired fields);
existing tests whose expectations encoded retired behaviour (each edit says why).

## Gates
Full suite; replay re-recorded; ruff/pyright on touched files; validator 0/0; `longhorizon --mode scripted` 0 engine
errors; the 7 real-save tests; the labelled cases C1-C29; Reader before/after on golden, held-out, goal-shape (+
goal-shape held-out after); one explorer playtest on Haiku (15 turns).

## Anti-pattern check (handoff §3.3)
- Code authoring narrative truth: Oracle draws about people are gone; "a smaller part of it" is gone; the `agreed`
  value is the act plus the Framer's own cited limit; the take-the-time RESULT states the time, not fiction.
- Over-triggering: Safe sourceless frames no longer roll; snags exclude Oracle answers; secret needs a learn goal.
- Blind model calls: the Framer now sees the target's licences; the fallback Framer sees its own scope.
- Low-precision blocking: the 01.9.3 form lists only re-route the close-call price, never block a frame.
- Mechanics as text: agreements are added, never overwritten.
- Test traps: cases labelled and committed (8619d6e) before code; Reader goal-shape held-out run after, untuned.
