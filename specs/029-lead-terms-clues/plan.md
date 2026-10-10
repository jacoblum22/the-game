# Plan 029: terms for every kind (T2) and one clue judgment per message (P9)

## Trace (round-8 saves, read-only; `playtest-20261010-0132*`)
- Talker [19]-[23]: `thr.lead_2` "A closed cart on the road at night" (the_prisoner's step-1 trace) has no
  `world.hook_terms` entry and no knower; the gate log is a narrator mention with no `text`; the turn stamped the
  question "(answered)".
- Explorer [18]: Betric (core holder of "who the challenger is") got `speech[:deliver_count(2, 2)]` = the banners part
  only; the clue call never saw the second part. [19]-[21]: `codex._about` resolved "The Long Downs" by alias, stopped,
  and never read said records or thread text.
- Fighter: `reduced_case` casts the duel's subject (Alred Millfield) from the locals, the opening only says "a quarrel
  turns to a challenge"; the Director staged a different youth.
- `world_step.deliver_learning`: `asked[:deliver_count(...)]` before `ans.ask`; `ask` calls `clue_case` per part; a
  fact answer is `e.learned` on a Talk beat but an `acts:` line (`answer_line`) for plain speech.

## Design
1. **Terms by kind** (`engine/gen/hooks.py` + `world_seed.yaml#terms`): a data entry per kind; `terms_for` builds, for
   each hook, `{hook, kind, family, what, where, who, words, doc, pay, know, fields}`. People are bound by id
   (reporter, witness, subject, contact, issuer's head), else a walk-on is created; documents (a gate log, a muster
   notice, a posted description...) are entities with a `text` fact made in the same pass. `write_terms` writes the
   typed meta, one `topic.hook.terms.*` fact per hook known by the knowers, the documents and the walk-ons.
   Lead injection (`write_injection`), rumors and creation hooks use the same builder.
2. **The actor on stage** (`incident.actor_on_stage`, `session.opening`): the subject of a duel, an offer or a
   refugees case (and the dead rider of a dying messenger) is added to the opening scene's cast by id; its aliases are
   the incident's role ("the challenger"); `name_known` stays false until the node is delivered.
3. **P9** (`answer.ask_message`, `world_step.deliver_learning`): typed routes per part (who-questions: no call), then
   **one** `clue_case` call over the remaining parts (the clue prompt takes a list; the output names the part), then
   `deliver_count` over the ordinary parts that remain. A delivered clue or pointer is a fact: `BeatEntry.learned` for
   a Talk beat, `AdjudicationRecord.learned` for plain speech (rendered by `handles.items` as a `learned` item); the
   line names no speaker. A part is marked answered only when a fact was delivered.
4. **The journal** (`codex.what_you_know`): split "X and Y"; for each piece search entities by alias and by words, thread
   *text*, knowledge records and the new **what you were told** (`testimony.told_to_pc`: said records with speaker, place
   and day), attributed.
5. Data: `world_seed.yaml#terms` (52 kinds), `investigation.yaml#journal` (fix the swallowed `journal.rumors` row).

## Files
`engine/gen/hooks.py` (grown), `case.py`, `cast.py`, `_seed_packs.py` (walk-on helper only), `world_seed.yaml`,
`investigation.yaml`; `engine/dm/answer.py`, `world_step.py` (`deliver_learning`, `_speech_answers`, `_look`),
`incident.py`, `codex.py`, `testimony.py` (place and day on a said record), `roles/clue.py`, `prompts/clue.md`,
`schemas.py` (clue schema), `llm/offline.py` (clue stub); one line each outside the lane: `adjudication.py`
(`record.learned`), `handles.py` (render it), `session.py` (the opening's cast), `world/pacing.py` (call
`write_injection`).

## Risks
- Parity: the seed record is untouched (terms are computed from the record on keyed streams; walk-ons for terms are
  created on a copy), so `12-world-seed.py` parity holds.
- The offline model must still pass the replay: the clue stub parses both message shapes.
- A new walk-on per kind adds entities: only the ones that hold or witness a term; counted in the results.
