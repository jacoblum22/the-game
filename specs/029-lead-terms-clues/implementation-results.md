# Implementation results 029: every lead and incident gets its terms when it is made (T2), one clue judgment per message (P9)

Branch `worktree-agent-ae4a0634713fbac11`, built on `milestone-1-playable` 119b64f (rules wave R2-L merged). Spec, plan,
tasks, the cases (`cases.md`) and the labelled multi-part clue set (`clue_set_multi.yaml`) were committed first
(b05e911); implementation f45e597; results and the merge after. Real numbers; nothing faked.

## Trace (round-8 saves `playtest-20261010-0132*`, read-only; before design)
- Talker [19]-[23]: `thr.lead_2` "A closed cart on the road at night" (the_prisoner's step-1 trace) had no
  `world.hook_terms` entry and no knower; the gate log was a narrator mention with no text; a licensed no-roll Observe
  carries the licence in `approach_words`, so `deliver_learning` (`v in approach_words`) delivered nothing; the turn then
  stamped the question "(answered)".
- Explorer turn.3: Betric (core holder of "who the challenger is") got `speech[:deliver_count(2, 2)]` = the banners
  part only; the clue call never saw "who the young man really is". Turn.4: `codex._about` resolved "The Long Downs" by
  alias and stopped; the thread was matched by its 60-character name; said records were never read.
- Fighter: `reduced_case` casts the duel's subject from the locals (Alred Millfield, at the hall); the opening said only
  "a quarrel turns to a challenge", so the Director staged a different youth.
- A plain-speech clue was an NPC "acts:" line naming a speaker (`answer_line`), a Talk beat's clue a `learned` line.

## What was built
| Fix | Where | What |
|---|---|---|
| Terms for every kind (T2) | `engine/gen/hooks.py`; data `rules/data/world_seed.yaml#terms` | One data entry per kind the game's data has (52: see below). The builder fills it from ids and names: **who** (the case's reporter and witness, cast people of the trade at the place, else a walk-on made for the term), **what**, **where**, the **words** of a document made in the same pass (a gate log, a price or road board, a muster notice, a writ, a missing notice, a stall tally, a letter, a token), the **pay** (a job fee), and who knows. Written as unsealed knowledge on the knowers' cards, in lines of at most 150 characters (the card cuts at 160 and shows five knowledge facts); the documents are `object` entities with a `text` fact, so reading one delivers its words; two entries for one gate are one gate log. No node answer is ever written (a test walks every incident). |
| Kinds covered | `hooks.kinds()` | **52** from the data: 8 incidents (`tbl.12.seed.inciting`), 16 situation traces (`world_turn.yaml#situation_templates`; lead 2 is a step-1 trace), 1 hire lead, 4 documents (`tbl.12.seed.document`), 12 lead-injection forms (`tbl.lead_injection`), 4 rumor kinds (a faction's goal, a situation's trace, a site, the keeper's dream), 7 creation-hook kinds (origins' `hooks`). `test_the_kinds_are_the_52_the_data_has` reads the tables and fails when a kind has no entry (or an entry no kind). |
| In play | `hooks.write_injection` (called once from `pacing.inject_lead`), `hooks.write_creation` (once from `creation.py`) | A lead injected in play and the PC's creation hooks get terms through the same builder: a bringer, overhearers, a found letter or token with its words, a trace, a contact who remembers, an informant and his price in favour, a petitioner; creation hooks bind the anchor bond for `npc`, else a cast person. |
| Actor on stage (X2) | `incident.stage_info/stage_actor`, `session.opening` (4 lines) | A duel's challenger, the one making the offer and the refugees' leader are the case's subject entity, moved to the opening place and added to the Director's cast **by id**; the opening note carries `the challenger: <their label>`; their name stays sealed until node 1 is told. The dying rider is a dead entity at the place. No other incident has a living actor. |
| One judgment per message (P9) | `answer.ask_message`, `clue_judgment`, `roles/clue.py`, `prompts/clue.md`, `schemas.clue_schema` (`{about, part}`) | Order: own-name and named-person parts (typed) -> **one** clue call over all other parts -> "who is <role>" parts (case graph / casting) -> `deliver_count` over the ordinary parts that remain. The call returns the clue and the question that asked it, so that question is not also answered ordinarily. `ask()` is a one-part message. |
| Clue delivery is a fact | `world_step.deliver_learning/_speech_answers/_give`, `AdjudicationRecord.learned`, `handles.items` | A delivered clue (or a non-holder's pointer) is a `learned` line with no speaker: on the Talk beat's `learned`, else on `record.learned` for plain speech (3 lines in `handles.py` render it as a must-name `learned` item). A part is marked answered only when a fact was delivered for it. |
| Learning keyed on the typed verb | `world_step.beat_verb`, `answer.willingness` | `BeatEntry.verb`, not `v in approach_words` (R8-I2 cause D). A document the beat reads is delivered whole (never cut at 120 characters). |
| The journal | `codex.what_you_know/journal`, `testimony.add_said` | "X and Y" is split (a name that is one entity's full name stays whole); each piece is searched over entities and aliases, **thread text**, knowledge records and said records; a **what you were told** section lists said records, attributed ("Betric Brightcote told you: ..."), with place and day, as testimony. The general journal lists it too. Said records now carry `place` and `day`. |
| Data fix | `rules/data/investigation.yaml` | The `journal.rumors` row had been swallowed by the comment after `journal.told` (R2-L); restored. `SCHEMAS.md` documents `terms`. |

## Retired
One-sentence leads and reporter-only incidents (every kind has its terms); the incident's actor invented by the
narrator or Director; per-part clue calls; `deliver_count` slicing parts before routing; first-question-wins routing;
a clue as an NPC "acts:" line; the journal's name-only short-circuit and thread-name matching; `v in approach_words`
learning; spec 025's rule that "last seen" has no term (superseded by "every kind").

## Gates
| Gate | Result |
|---|---|
| Full suite | see the final run below |
| Replay | re-recorded (`offline_seed11`); passes |
| ruff / pyright (touched files) | 0 / 0 (pyright with the project interpreter). `ruff check` over the repo still shows 4 pre-existing E741 in `evals/orchestration/resolve_rules_merge.py` (not touched) |
| Validator | **0 ERROR / 0 WARN** (INFO only; ids defined 3708, the restored journal row) |
| `longhorizon.py --mode scripted` | **0 engine errors** (389 turns, 314 narrated; `longhorizon_scripted.txt`) |
| Round-8 saves (`replay_r8.txt`, Haiku) | see the next section |
| Clue judgment, Haiku (`clue_eval_multi_haiku.txt`) | spec-025 set: **precision 1.00 (17/17), recall 0.94 (17/18)**; 20 new multi-part messages (labelled before the run): **precision 0.92 (12/13), recall 1.00 (12/12)**; the question that asks it named on 11/12; all 56: precision 0.97, recall 0.97 |
| Live, Haiku engine, Sonnet player, explorer, 15 turns | see below |

### Round-8 saves
- **Talker (gate log).** A new game writes the gate log with the cart lead; on the save cut before turn.4 the log's text is
  "Entry, the spring quarter day, after dusk: One closed cart through the gate, ... It took the road to The Grey Leas. Passed on
  the word of the Crowbridge Circle's runner. Entered by Helian Lanent."; the licensed no-roll Observe (`lic.lang.letters`) now
  reads as `verb.observe`; the read delivers those words whole; both parts are marked answered because a fact came. The
  captain's card holds what, whose, the driver and who saw it. **Pass.**
- **Explorer turn.3 (Betric).** Both parts reach one judgment (Haiku: clue 1, question 2); `record.learned` =
  "who the challenger is: Falbo Bramblewick"; the banners part is answered ordinarily; no NPC line carries the clue; only
  the second part is marked answered. The cap no longer decides it. **Pass.**
- **Explorer turn.4 (journal).** "What do I know about the Long Downs and the winter that brought the realm down?" lists the
  place, the wound thread (by its text) and "Betric Brightcote told you: The banners are the old colours of the Long Downs,
  from before the winter that brought the realm down". **Pass.**
- **Fighter.** The same world, a new opening: the case's challenger (Alred Millfield) is in the scene's cast, at the inn,
  labelled "the challenger: the officer" in the opening note, name sealed. **Pass.**

## Made-up and edge cases, one by one (labels in `cases.md`; tests in `tests/engine/test_spec029_cases.py`, 83)
K1-K8 incidents (data-enumerated) pass, each with its card lines and no sealed answer on any of them; K9-K24 the sixteen
situation traces pass (documents where the words are held); K25 hire; K26-K29 the four documents; K30-K41 the twelve
injection forms; K42-K45 the four rumor kinds; K46-K52 the seven creation hooks; P1-P6 (gate log, closed cart, banners,
fighter's challenger, winter and banners, Betric) pass; C1-C10 (clue second, clue third at Limited reach, one call whatever
the parts, a sound-alike, an Unfriendly holder, a found clue, an absent holder, speech with no beat, answered stamps, a
typed part beside an ordinary one) pass; J1-J5 (the miller's daughter, X and Y, contradicting speakers, nothing known, a
name that contains "and") pass; S1 (nothing sealed) passes.

## Analysis (spec-kit analyze, cross-artifact)
- Every user story has accept cases and every case id (K1-K52, P1-P6, C1-C10, J1-J5, S1) has a test; the 52 data kinds
  are walked from the tables, not listed in the test. Tasks T1-T10 are all done.
- Where the plan was changed while building: (1) the journal's attributed lookup lives in `codex.py`, not
  `testimony.told_to_pc` (testimony only gained `place` and `day`); (2) the clue schema's `part` is required, not
  optional (the project's schema contract); (3) the actor's role is carried by the opening note's `the challenger: <label>`
  field, not by an alias on the entity (an existing person's record cannot be amended after the seed writes it); (4) term
  lines are chunked to 150 characters (the card cut) rather than one fact per hook; (5) `deliver_learning` keys on the typed
  verb, which the brief's lane note implied (R8-I2 cause D) but the plan did not list.
- No conflict with the constitution: VIII.1 (the terms are data fields, the words of documents are the owner-approved
  "words of any document or message"), VIII.4 (the clue call reads the whole message), VIII.6 (the clue prompt gets only
  the about lines).

## Anti-pattern check (handoff 3.3)
- **Code authoring narrative truth.** The terms are the owner-approved T2: short data fields filled from ids, never a
  sentence the narrator is made to repeat. Five lists hold invented content: the rider's last words, the challenge, the
  refugees' story, an omen's sign and the documents' texts (the owner asked for "the words of any document or message").
  They are picks from short data lists on the hook's own stream.
- **Over-triggering.** One clue call per message with questions while a case has an open node, however many parts.
- **Low-precision checks that block.** None added.
- **Blind calls.** The clue call sees the questions, the last exchange and the about lines, never an answer.
- **Test traps.** The multi-part set was labelled and committed before the prompt was run; the prompt's new example
  ("the lamp oil") is not in either set.

## Hand-offs
- **Spec 028 (`narrator.py`, `handles.py`, `packet.py`, `turn.py`, Reader)**: (1) `handles.py`: three lines render
  `record.learned` as a must-name `learned` item (keep them when `npc` items change); (2) `turn.py` still stamps every
  FICTION_QUESTION "answered" unconditionally; the learning path now sets `handled = "answered"` only where a fact was
  delivered, so removing the stamp is safe; (3) `narrator._reading_lines` should include the beat's **target** and read
  `written_words` first (the gate log now has text), and the single-written-thing fallback can go; (4) `packet.speaker_card`
  cuts a line at 160 characters and shows five knowledge facts: term lines are cut to 150 to fit, so a longer cut or a
  higher cap lets cards carry more; "places this person knows" can use the rumor terms (`points toward`); (5) the opening
  note carries `the challenger: <label>` (and `<label>: lies dead in the scene`) from `incident_line`: the narrator should
  use it instead of inventing the actor.
- **Spec 030 (`audit/`)**: `claims.py:1018` reads `b.learned` only; it should read `record.learned` too.
- **Rules**: nothing blocks. SCHEMAS.md now lists `terms`.

## Assumptions
As recorded in `spec.md` A1-A5, plus: A6 term lines are cut to 150 characters because the card cuts at 160 and shows five
knowledge facts; A7 a holder with no cast person of the trade at the place is a walk-on made for the term (two or three per
world; the cart's driver and a "wrong man sent" are made but not placed); A8 the clue schema's `part` is required (the
project's schema contract), so test doubles must give it.
