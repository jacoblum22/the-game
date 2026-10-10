# Plan 024: stop pushing texture, one outcome, the passage as written

## Trace first (done before design, on copies of the round-7 saves `playtest-20261009-1606*`)
- **Standing-line inventory** (scratch `standing.py`: every VIEW and THIS MESSAGE line repeated verbatim in 3+ narrator
  packets of a save). Talker: "the matter at hand … Kerric Hartsmith brought the word." 15/15; `voice: register=cold,
  habit=counts on their fingers while thinking` 6/6 of the gate scene; `present: … (she/her, middle-aged, a finely
  embroidered collar, suspicious)` every later turn; `call them "the sellsword between contracts", as every other
  screen does` 9/9; "young (in their teens)", "jewelry too fine for their station". Explorer: the incident line 15/15;
  `voice: … habit=calls everyone by a nickname` 11; the look on `present:` 11. Fighter: the incident line 14/14;
  "call them" ×3 per packet; "the officer of The Kingsholt Company of Merchants".
- **Talker turn.12 (input 27)**: `R1 MUST: … result: failure (the world answers), a near miss` while the pause is open,
  with the generic answer line ("never end on waiting for them to speak"). **Turn.13 (input 28)**: R1 "success at
  cost … never a refusal", R3 "refuses, in their own voice (jovial, whispers secrets far too loudly): the talk did not
  move them (failure)": `npc_layer.py:570-575` reads `entry.degree` only.
- **Explorer turn.4/turn.5 (inputs 20-21)**: the recorded passages have `\n\n` paragraph breaks; the deliveries have
  none (`narration._text` joins `sentences_of` with spaces).
- **Fighter turn.1**: `the character cannot read the any posted notice`; the opening's R2 note ends "Magby Applefoot
  brought the word"; R3/R4 are the seed's lead sentences verbatim.

## The push inventory (every code-supplied texture line, and every instruction that forces texture)
| # | Surface | Where | Done |
|---|---|---|---|
| 1 | `voice: register=…, habit=…` raw in every view | `packet._entity_lines` | one `background` line, habit "now and then", pronouns filled |
| 2 | `detail:` / `demeanor:` raw in every view | `packet._entity_lines` | in the same background line |
| 3 | look on every `present:` line | `packet.scene_setting` | look only when the place is described (`full`) |
| 4 | "people here … so show how they look and stand" | `packet.scene_setting` header | "how they look is yours to use or leave" |
| 5 | `call them "X", as every other screen does` | `packet.scene_setting` | "name not known to the character" |
| 6 | `call them "X" (the words every other screen uses; add how they look if you like)` | `packet._entity_lines` | "does not know her name: never by a name until she gives it" |
| 7 | "the matter at hand: X brought the word." every turn | `packet.scene_setting` ← `incident.incident_line` | removed; `incident_line` returns data ("reported by: X") for the opening note only |
| 8 | FRESHNESS openings quote-back | `narrator.freshness_lines` | removed |
| 9 | "Details stated lately" (usage marks) | `narrator.used_details`, `narration._mark_used` | removed (no marks written) |
| 10 | "Lines these people already said lately" (speech openers) | `narrator._repeated_lines` | removed (said records stay on the speaker card: an NPC never repeats its own said line, 12.14.11) |
| 11 | habit in refusal lines | `npc_layer.voiced_refusal` | register only, pronouns |
| 12 | "in their own words / voice" in willingness lines | `answer.WILL_WORDS` (both format sites) | the NPC's pronouns |
| 13 | "the talk did not move them" | `npc_layer`, `answer.willingness` | pronouns |
| 14 | activity and response rows "their morning work", "back to their activity" | `npc_layer.ensure_activities`, `scene_state.write` | pronouns at write; and at render for old saves |
| 15 | NPC act lines ("carries on with their own business") | `narrator._item_words` | pronouns |
| 16 | `_withheld` gesture suffix on non-refusals (P4) | `narrator._withheld` | refusals only |
| 17 | "the one impetus the record names" (scene_open) | `narrator.PURPOSE_LINES`, prompt | "any impetus the record names" |
| 18 | seed lead sentences as MUST notes ("folk say it is only the beginning") | `session.opening` notes ← generator | narrator words the note as a gist: "a lead to make noticeable (its gist, in your own words …)"; generator hand-off to 025 |
| 19 | public news on the speaker card (the seed's situation sentence, spoken verbatim by Kerric) | `packet.speaker_card` | labelled "the gist; never these words" |
| 20 | "do not repeat a line you already used" on OPTIONAL MATERIAL | `narrator.optional_material` | "an unchanged line need not be said again" (12.14.12 wording) |
| 21 | the prompt: no statement that looks and habits are optional | `prompts/narrator.md` | one neutral line: background, use or leave out |
| 22 | "the any posted notice" (P5) | `narrator._reading_lines` | grammar |

Kept, with reasons: the `said` records on the speaker card (dialogue memory, 12.14.11 "said lines"); the view's
`detail.*` scene-state facts (data, no instruction; activity lines are offered once by spec 013); place looks after
framing (already dropped, DL-12-99); the closing "unresolved image" (12.14.9 allows it; copying forward is the
narrator's judgment, ruled so).

## Design
| Piece | Where | What |
|---|---|---|
| One outcome | `dm/adjudication.py` | `undecided(b, pause)` (moved from `audit/claims.py`) and `effective_degree(b, pause=None)` |
| Readers | `npc_layer`, `answer`, `scene_state`, `world_step._ok`, `roles/narrator`, `handles`, `audit/claims`, `audit/fallback` | read `effective_degree` / `undecided` |
| Paused beat | `roles/narrator._beat_line`, `_speech_line`; `handles.items` | no result words, not owed; the paused ask's target has not answered yet |
| Pronouns | `dm/packet.py` `pronoun_words(state, eid)`, `own_words(text, pron)` | one helper for every template |
| Delivery | `dm/narration.py` `_text(sents, source)` | sentences located in the passage in order; gaps (paragraphs) kept; cuts close their gap |
| P5 | `audit/claims._pronoun_hit` + `precision_checks(speaker=)`; `rules/data/world_seed.yaml` doc rows; `roles/narrator._reading_lines` | tag pronoun judged against the declared speaker |
| P6 | `evals/longhorizon.py` | offline narration lines labelled stub plumbing |
| Data | `pacing.yaml` (delete retired keys), `oracles.yaml` (pronoun-fill rule lines on the person tables), `world_seed.yaml` | `[revision: R2-K]` |

Justifications outside the listed lane (one line each): `dm/adjudication.py` holds `BeatEntry`, so the one outcome
function lives beside it; `dm/handles.py` renders the beat line the narrator is shown (T4's paused beat);
`dm/world_step._ok` is a degree reader (T4: every reader); `rules/data/world_seed.yaml` holds the notice template (P5).

## Gates
Full suite; replay re-recorded; ruff and pyright on touched files; validator 0/0; `longhorizon --mode scripted` 0
engine errors; the round-7 packets rebuilt (`replay_r7.py`); every case in `cases.md` as a test; one live talker
playtest on Haiku (≤15 turns, player on Sonnet) measured by `measure.py`.

## Anti-pattern check (HANDOFF §3.3)
- **Mandatory texture**: removed at every surface in the inventory; no instruction requires a look, habit or gesture.
- **Code authoring narrative truth**: the incident sentence, the verbatim label and the pronoun-neutral templates are
  gone; the reporter and the faction are data; leads and news are gists.
- **Mechanics stored as text**: the paused beat carries no result words; NPC reactions read the effective degree.
- **Atomisation**: the sentence split is an index into the passage, no longer the delivered text.
- **Low-precision blocking checks**: the pronoun check no longer judges a speech tag by the last-named person.
- **Over-triggering rules**: READING lines need a written thing named or acted on.
- **Test traps**: offline narration metrics labelled as stub plumbing; the repetition measure reads live saves.
- **New tracking**: none added (owner ruling); usage marks removed.
