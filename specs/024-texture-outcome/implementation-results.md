# Implementation results 024: stop pushing texture (T3), one outcome (T4), P1, P4, P5, P6

Branch `worktree-agent-a9b07c2196a359020`, built on `milestone-1-playable` c8788a1 (R2-K merged). Cases committed
first (9ab4db2), implementation 001bb3d, results and two wording fixes after the live run. Real numbers; nothing
faked.

## Trace (before design)
On copies of the round-7 saves: the standing-line inventory (`plan.md`), talker turn.12/13 (the near miss written as
"failure, a near miss" before the choice; the refusal from `npc_layer.py:570-575` reading the raw degree), explorer
turn.4 (21 of 43 passages had paragraph breaks, 0 of 43 deliveries), fighter turn.1 ("the any posted notice", the
incident note "brought the word", seed lead sentences as MUST notes).

## Every push removed (the inventory, `plan.md` table)
1. raw `voice:` (habit) in every view → one `background (use or leave out as you like; nothing requires it)` line:
   look, manner, voice; the habit "now and then …"; the person's pronouns.
2. raw `detail:` / `demeanor:` → the same background line.
3. the look on every SCENE SETTING `present:` line → only when the place is described (framing, looking around).
4. "so show how they look and stand" → "how they look is yours to use or leave".
5. `call them "X", as every other screen does` → "name not known to the character".
6. `call them "X" (the words every other screen uses; add how they look if you like)` → "does not know her name: never
   call her by a name …".
7. "the matter at hand: X brought the word." in every SCENE SETTING → removed; `incident_line` returns data
   (`reporter: X`) for the opening note only.
8. FRESHNESS openings quote-back, 9. "Details stated lately" (usage marks, `_mark_used`, `used_details`), 10. "Lines
   these people already said lately" (`_repeated_lines`) → deleted. No marks are written.
11. the habit inside refusal lines → register only. 12. "in their own words/voice" (willingness) and 13. "the talk did
   not move them" → the NPC's pronouns. 14. activity and response rows ("their morning work") → pronouns at write and
   at render. 15. NPC act lines ("carries on with their own business") → pronouns.
16. P4: the `_withheld` gesture suffix → refusals only. 17. "the one impetus the record names" → "any impetus".
18. seed lead notes → "a lead to make noticeable (its gist, in your own words or a speaker's)". 19. public news on the
   speaker card → "the gist; in the speaker's own words, never these". 20. "do not repeat a line you already used" on
   optional material → "an unchanged line need not be said again". 21. the prompt: one neutral line on the background.
22. "the any posted notice" (P5). After the live run: "they already said" (speaker card header and the said-line
   redraft) → the speaker's name.

Kept with reasons: `said` records on the speaker card (dialogue memory, 12.14.11); the view's `detail.*` scene facts
(data, no instruction); the closing "unresolved image" (12.14.9 allows it).

## T4, P1, P5, P6
- `effective_degree`, `undecided`, `paused_beat` in `dm/adjudication.py`; read by `npc_layer` (talk outcome and the
  response row's degree), `answer.willingness`, `scene_state._band`, `world_step._ok`, `audit/claims._beat_success`,
  `audit/fallback._beat_line`, `handles.items`, the narrator's beat and reading lines. A paused beat has no degree,
  no "near miss", no result words, is not owed, and its target "has not answered what the paused beat asks yet".
- P1: `narration._text(sents, source)` places each kept sentence in the passage with the whitespace before it; a cut
  takes its gap and passes a paragraph break on; code quoting is in place; rendered lines join with a space.
- P5: `Posted by {issuer}.` (world_seed.yaml; the example seed regenerated); the pronoun check judges a speech tag
  against the declared speaker (no verdict without one); READING lines need a written thing named or acted on.
- P6: offline novelty-4 and narration-loop lines are printed as "[offline stub: plumbing only, NOT a narration
  measure …]".
- Data `[revision: R2-K]`: `habit_max_per_scene` and the retired freshness keys deleted (`freshness: {said_overlap,
  setting_once, repetition_scan: log_only, scan_window}`); pronoun-fill notes on `tbl.npc_age`, `tbl.npc_detail`,
  `tbl.npc_activity`, `tbl.npc_voice_habit`.

## Gates
| Gate | Result |
|---|---|
| Full suite | **1818 passed, 4 skipped** (after the last change) |
| Replay | re-recorded (`offline_seed11`); passes |
| ruff / pyright (touched files) | 0 / 0 |
| Validator | **0 ERROR / 0 WARN** (INFO only: BASIS 1, POOLS 2, REFS-EX 9, REFS-MD-EX 70) |
| `longhorizon --mode scripted` | **0 engine errors** (`longhorizon_scripted.txt`) |
| Made-up and edge cases | **25 of 25 pass** (16 tests in `tests/engine/test_spec024_cases.py`, plus `test_incident` C19 and `replay_r7.py` C10/C24/C25) |
| Round-7 packets rebuilt (`replay_r7.txt`) | talker / explorer / fighter, as played → rebuilt: habit outside background 16/15/14 → **0/0/0**; "brought the word" 16/16/14 → **0**; freshness quote-back 19/14/15 → **0**; `call them "…"` 36/18/52 → **0**; pronoun-neutral templates beside a he/she person 63/19/58 → **0** |
| Talker input 27 (turn.12) | R1 "result: failure …, a near miss" → "not resolved yet: the player chooses next …"; "the sellsword has not answered what the paused beat asks yet" |
| Talker input 28 (turn.13) | R3 "refuses, in their own voice (jovial, whispers secrets far too loudly) …" → "takes what you offer and agrees to what you ask" (R2's cost "he turns the round down" still contradicts it: hand-off to 023) |
| Explorer inputs 19-21 (turn.4-6) | paragraph breaks in the passage 2/0/0, delivered in round 7 0/0/0, delivered now 2/0/0 (identical to the passage) |

Cases, one by one (labels in `cases.md`): C1 innkeeper ten turns incl. fire, pass (habit only in the background line,
10/10 first drafts) · C2 guild label, pass · C3 lock near miss, pass · C4 he/him walk-on, pass · C5 near miss then
something new, pass · C6 "what did the notice say again?", pass · C7 habit twice knowingly, pass · C8 fire, pass ·
C9 she/her unnamed, pass · C10 accepted near miss then willingness, pass (unit and round-7 replay) · C11 paused beat at
an OFFER and a near miss, pass · C12 two paragraphs two speakers, pass · C13 habit across three scenes, pass · C14
"any posted notice", pass · C15 notice separator, pass · C16 speech-tag pronoun, pass · C17 "what did they say?",
pass · C18 P4, pass · C19 no incident sentence, pass · C20 cut opening a paragraph, pass · C21 degrees, pass · C22
they/them and unrecorded, pass · C23 free text untouched, pass · C24 explorer paragraphs, pass · C25 rebuilt packets,
pass.

## Live: one talker playtest on Haiku (player Sonnet), 15 turns (`evals/playtests/20261009-201430-claude-talker.md`)
`measure.py` on the save (`measure_live_talker.txt`; round-7 baselines by the same script in
`measure_r7_baseline.txt`):
- **Habit per NPC**: Dushra (swears by a saint) 0 of 6 speaking turns; Laethas (counts on fingers) 1 of 1. Round 7 by
  the same measure: Kerric 3 of 5, the sellsword 2 of 5, Belie 2 of 2 (hand count, I1: 16 of 21).
- **Look per NPC**: Grza's "long scar along the jaw" **7 of 9** of her speaking turns ("the scar along her jaw
  pulls"); Dushra's height 0 of 6. Round 7: the sellsword's scar 5 of 5, Morga's 5 of 8.
- **Model-made images**: the hiring bill "lifts in the draught" in 10 of 16 deliveries, the porridge in 6. These come
  from the narrator's own written-on-mention facts (`item.hiring_bill_on_the_doorpost`: text, location;
  `obj.cooking_pot`: "where Dushra stirs the porridge"), which stand in every later view's `facts:`, plus RECENT
  EXCHANGES. The player flagged the bill in 8 notes and the scar once. Image carry-over 9 of 15 (round 7 talker 10 of
  14).
- **Code sentences leaked**: 3, all the seed lead "the Marlcrag Moot is hiring, and asks no questions" (the opening
  note, the bill's narrated text, an overheard line). No "brought the word", no "officer of The".
- **Pronoun drift**: 0 (pronoun check 0 hits; 2 "they" candidates, both plural objects, coins).
- **Misattributed speech**: 0 candidates; 16 of 16 deliveries keep paragraph breaks.
- **First draft** 13 of 16 (81%): 2 revisions from the numeral check on the player's own offers ("ten", "fifteen"
  silver), 1 from not_a_repeat. Narrator calls 1.19 per narrated turn; all model calls 3.06.

**Read plainly:** the pushes are gone and so are the habit tics, the code sentences (except the seed lead) and the
pronoun drift. Repetition is not gone: a look given as background, and images the narrator itself wrote into the store,
still come back most turns. DL-12-113's "revisit if" is met (a look in more than 1 of 3 speaking turns). See the
owner decision.

## Retired
`incident_line` in scene settings; the raw voice/detail push; the look on later `present:` lines; the habit in
`voiced_refusal`; `freshness_lines`, `_repeated_lines`, `_freshness`, `used_details`, `_mark_used`, `_Sent.used`;
"call them … every other screen"; pronoun-neutral template strings; "result: failure, a near miss" before the choice;
degree-only reads in the readers listed; `_text`'s space join; `habit_max_per_scene` and the retired freshness keys.
Left for old saves only: the `details_used` event type and `store.details.used_event` (no longer emitted).

## Hand-offs
- **Spec 023**: `turn.py:913` and `resolve/pipeline.py` (204, 546, 777, 887) still read `degree`/`success_at_cost` by
  hand: switch to `effective_degree`. The cost menu priced talker input 28 with "he turns the round down", which
  reverses the goal (01.9.3 check). `retrieve/scene.READING` (used by `gate.py:360`) matches "what did they say" and
  misses "what did the ferry notice say": the narrator now guards itself; the gate does not. The numeral check blocks
  the player's own offered sums ("ten silver"): 2 of 3 live revisions.
- **Spec 025**: the seed's lead sentences ("…, and asks no questions", "folk say it is only the beginning",
  `_seed_steps.py:787, 859`) and role strings "officer of {faction}" (`:517`) should be data (T2 terms; role +
  `member_of`); the live run's only code-sentence leaks were the lead. Seeded voice/detail rows are stored with
  "their" (`_seed_lib.py:340`); the engine fills pronouns at render, the seed could fill them at write. P3 still open.
- **Spec 026**: `fixer.py:173` prints the raw degree in turn listings; show "success at a cost" (effective degree).

## Assumptions (recorded, no clarify step)
See `spec.md`: background stays in the view once per packet; the repetition scan is `measure.py`, run on saves, not
engine code; generator text is neutralised on the narrator side and handed off; pronoun fill only on template text
and only their/them/themselves/theirs; the goal-reversing cost is 023's.

## Owner decision
**The look and the narrator's own images still repeat with nothing pushing them.** In the live run the scholar's scar
came back in 7 of her 9 speaking turns and the hiring bill "lifting in the draught" in 10 of 16 turns; the player
called both stale. Nothing tells the narrator to use them now: they sit in the packet as background (her look) and as
facts the narrator itself wrote earlier (the bill, the porridge), and it reaches for them to fill the closing image.
- (A) Leave it, per the T3 ruling, and measure again next round.
- (B) "Setting once" for people and narrated scenery, the rule places already follow (DL-12-99): a person's look and
  the scene's narrated images reach the narrator when the scene opens, when that person first appears, or when the
  player looks or asks. After that they leave the packet and stay in the store. Nothing is counted or marked: it is a
  rule about *when* data is shown, not about how often it was used.
- (C) Bring back a logged quote-back of recent closing images (the narrator is told what it just ended on). This is
  closer to the tracking the ruling declined.

**Recommendation: B.** It treats people like places, adds no tracking, and removes the standing material the live
repeats came from. If the owner agrees, it is a small packet change plus a 12.14.11 wording change.
