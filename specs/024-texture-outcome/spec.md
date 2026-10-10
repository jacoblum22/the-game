# Feature spec 024: stop pushing texture (T3), one outcome (T4), patches P1, P4, P5, P6

**Input**: `research_notes/Playtest round 2 solutions/ROUND7-PLAN.md` (T3, T4, P1, P4-P6, owner rulings);
ROUND7-ANALYSIS §2 T3, T4, §3, §6; `rules/_process/reports/R2-K-report.md`, "Spec 024" checklist; traces
`round7-investigation/R7-I1-narration.md` §1-6 and `R7-H1-repetition-history.md`. Rules: 12.11.3, 12.11.9 step 4,
12.14.11, 12.2.4, 00.6.6a items 3 and 5, PR-12-1 T12, 12.16.16, 12.11.1; 01.9.3, 12.2.6, 12.14.12, PR-12-2.
DL-12-113, DL-12-114, DL-12-115, DL-01-48. `pacing.yaml#npc.habit_phrasing`, `#narration.freshness`;
`oracles.yaml#tbl.npc_voice_habit`.

**Owner ruling on T3 (binding)**: "If it wants to mention the look or habit more than once, and it's aware that it
already used it, then I think it's fine if it uses it more than once. I don't think we should prevent it or encourage
it." So T3 removes every push and adds **no** usage tracking, no once-per-scene gate and no new mechanism. The
narrator already sees the last 4 exchanges.

**Parallel lane**: spec 023 (question owners, goal checks, take the time) runs beside this one. Not ours:
`engine/resolve/`, `turn.py`, `oof.py`, the Reader and Framer, the generators and willingness logic (spec 025).

## User stories

### US1 - Nothing in the packet pushes a look, a habit or a code sentence (P1; T3; DL-12-113, DL-12-114)
Every code-supplied texture line in the narrator packet, and every instruction that forces texture, is removed or
neutralised (the full inventory is in plan.md). A person's look, manner and voice reach the narrator once per packet
as one **background** line in the view ("may use or leave out; nothing requires it"), the habit worded as occasional;
the SCENE SETTING `present:` line carries the look only when the place is described (scene opening, looking around),
otherwise name, role and pronouns. No FRESHNESS block, no "details stated lately", no quoted-back openings or
speech openers, no usage marks. No "X brought the word" in any scene setting; the incident's reporter is a data
field of the opening note. No "call them '…', as every other screen does": an unnamed person is described in the
narrator's own words. Code-written text about a person uses their stored pronouns.
- **Accept**: the round-7 talker and explorer narrator packets, rebuilt with the new builder, hold 0 habit lines
  outside the background line, 0 "brought the word", 0 FRESHNESS / quote-back lines, 0 "call them" lines and 0
  pronoun-neutral template words for a person with stored pronouns.

### US2 - One outcome (P1; T4; DL-01-48, DL-12-115)
One function, `effective_degree`, gives a beat's outcome: a success at a cost taken is `success`; a beat paused before
its choice has none. Every reader uses it: the NPC's response (`npc_layer`), willingness (`answer`), scene state
(`scene_state`), the narrator's beat line and reading line, the claim checks, `world_step`'s learning gate. A paused
beat is unresolved in the narrator's record until the player chooses: no degree, no "near miss", no result words,
not owed, and the addressed NPC has not answered the paused ask yet.
- **Accept**: talker input 27 (turn.12) rebuilt: no "failure", no "near miss" in THIS MESSAGE; input 28 (turn.13)
  replayed through `npc_layer.respond` and `answer.willingness`: no refusal line, willing.

### US3 - Deliver the passage as written (P1 patch)
The delivered fiction is the model's passage with its paragraphs; cuts, code quoting and rendered lines are applied in
place; a cut sentence that opened a paragraph leaves the break to the next kept sentence.
- **Accept**: explorer inputs 20-21 (turn.4, turn.5) delivered from their recorded passages keep their `\n\n`.

### US4 - Patches P4, P5, P6
- P4: `narrator._withheld`'s "do not give the PC what was asked" suffix only on a refusal.
- P5: "the any posted notice" grammar; the notice signature separated ("Posted by …"); the pronoun check judges a
  speech tag ("she says") against the declared speaker, never the last-named person; `READING` lines only for a
  written thing named or acted on (never "what did they say" with no document named).
- P6: offline narration metrics are labelled as stub plumbing in `evals/longhorizon.py`, not narration measures.

## Retired (each says what supersedes it)
- `incident_line` in every SCENE SETTING → the reporter as a data field of the opening note only.
- The raw `voice:` / `detail:` / `demeanor:` push → one background line, the habit occasional.
- The look on every `present:` line → only when the place is described (DL-12-99's setting once, extended to people).
- The habit in `voiced_refusal` → register only.
- `_mark_used`, `used_details`, `freshness_lines`, `_repeated_lines`, `_freshness` → nothing (12.14.11: the narrator
  judges from the conversation it sees). `pacing.yaml` `habit_max_per_scene` and the retired freshness keys deleted.
- "call them '…', as every other screen does" and "the words every other screen uses; add how they look" → none.
- Pronoun-neutral template strings for a person with stored pronouns → their pronouns.
- "result: failure, a near miss" before the choice; degree-only checks → `effective_degree`.
- `_text`'s space-join as delivery → the passage as written.

## Assumptions (no clarify step; recorded here)
1. "Background" means the data stays in the view once per packet, labelled optional; it is neither removed (the
   narrator needs who it is talking about) nor offered once per scene (that would be tracking, ruled out).
2. The repetition scan 12.14.11 keeps "logged as a measure" is this spec's measurement script
   (`specs/024-texture-outcome/measure.py`), run on saves each round; no engine code computes it per turn
   (VIII.5: no new procedure where removal suffices).
3. The seed's lead sentences ("folk say it is only the beginning", "is hiring, and asks no questions") and the seeded
   role string "officer of The …" are generator output (spec 025's lane). Here they are neutralised on the
   narrator side (a lead note is a gist to word freely; no verbatim-label instruction); the generator fix is handed
   off.
4. Pronoun fill replaces only `their`, `theirs`, `them`, `themselves` in template-derived text (table rows: look,
   age, habit, activity, response rows, record-line templates), never free text such as knowledge or leads, and
   never `they` (verb agreement). Unrecorded or they/them pronouns leave the text as it is.
5. The cost menu that prices a talk with "he turns the round down" (talker turn.13 R2) reverses the goal; that is
   01.9.3's price check, spec 023's (T5). Here the NPC response no longer adds a refusal on top of it.
