# Data model: spec 006

No new event types and no stored-state migration (DL-12-40..43 "Migration: none").

| Entity | Fields | Where |
|---|---|---|
| `RecordItem` | `handle` (`R1…`), `kind` (beat, cost, harm, condition, position, learned, oracle, npc, activity, omen, note, scene), `must_name`, `entities` [ids], `words` (the narrator's line), `render` (code-built statement or ""), `beat` (index or None) | `engine/dm/handles.py` (derived, never stored) |
| `NewElement` | `element_kind` (closed list), `name`, `ordinary`, `implied` [{predicate, value}] | `engine/audit/declare.py` |
| `DeclaredSentence` | `text`, `refs` [handle or fact id], `about` [ids], `new` [NewElement], `atmosphere` | same |
| `SentenceCheck` | `index`, `ok`, `failures` [{why, fix: cut/redraft/oracle, store_value}], `added_about` [ids], `undeclared` count | same |
| Activity (T1c) | fact `activity` = text on the NPC; current iff `valid_from_seq >= scene.started_seq` | store |
| Spoken-with | meta `npc.spoken` = `{scene, npcs: [ids]}` | store |
| Voice (walk-on) | fact `voice` = `{register, habit}`, rolled on first answer | store |
| T1a detail | fact `<predicate>` = value, source `narration` (written as narrated) | store |
| NPC response | `NpcActionEntry` (unchanged fields; `source` `table_row`/`talk_outcome`/`refusal`/`want`; `tags` holds the practice) | adjudication record |

Draft versions in `TurnRecord.draft_versions` gain `sentences` (declarations) and per-sentence `checks`;
`kind` is `draft`, `repair`, `cut`, `render` or `fallback`.
