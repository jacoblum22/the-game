# Spec 032 P7: the confirming head-to-head (scoring)

Six persona runs (talker, fighter, explorer, each on the pipeline and on dm-tools; 15 engine turns each; Haiku engine, Sonnet player,
`--quick-setup`), the 60-line scripted dm-tools run, and the NPC-agency "after" tables, scored by `evals/h2h_score.py`, by hand, and by
reading the saves. Nothing was re-run live. The default engine was not changed. The held-out set (C11) has a runner but has not been
run yet.

## Verdict (plain words)

dm-tools is much cheaper and faster, and in these six runs it was no worse on mistakes. It used 0.40x the input tokens of the pipeline
per turn (18.2k against 45.6k) and 0.46x the model time (16.8 s against 36.7 s), with 1.9 model calls a turn against 3.4. By hand count
it had 5 contradictions to the pipeline's 8, no wrong speaker (the pipeline had 1, a dead woman speaking), and 1 `/fix` request to the
pipeline's 6. The fight worked: the foe acted on every exchange where the player's roll was settled (3 of 3). No secret leaked.
But I cannot say "all gates pass", for two reasons. First, the held-out set (C11) has not been run; I built the runner, and by
reading the code I expect it to fail the "sneak at a person only described in prose" and "observe a person only described in prose"
items, because the live talker run hit exactly that refusal. Second, C9 fails on its strict reading: dm-tools wrote 22 "what you
were told" records but dropped 28 lines people said, 18 of them from the talker's main NPC, who walked beside the player in the story
but was still recorded at the place they had left, and 5 from people the DM described but never made. Two bugs, both traced below. My
recommendation is not to flip the default yet; both bugs look small, and the cost and fight results are strong enough to be worth the
fixes and one more look.

## Gate table (C1-C11)

| Gate | Measure | Result | Pass rule | Status |
|---|---|---|---|---|
| C1 cost | tokens in per engine turn, dm-tools / pipeline | 18,208 / 45,580 = **0.40** | at most 0.6 | PASS |
| C2 speed | model latency per engine turn | 16.8 s / 36.7 s = **0.46** | at most 0.7 | PASS |
| C3 contradictions | hand count, 3 personas x 15 turns | dm-tools **5**, pipeline **8** | dm-tools at most the pipeline | PASS (small numbers) |
| C4 `/fix` load | `/fix` reports per arm | dm-tools **1**, pipeline **6** | at most the pipeline's | PASS |
| C5 pushover | costly asks granted, mood changes with no event | observed, not gated: see section 4 | n/a [owner ruling 2026-10-10] | OBSERVED |
| C6 mood held | in-character refusals, repeat-ask caving | observed, not gated: refusals 5/6 vs 11/13, caving 0/4 vs 1/4 | n/a [owner ruling 2026-10-10] | OBSERVED |
| C7 leaks | real secret leaks | **0** (persona saves 0 logged; the agency run flagged 1, a false positive, section 4) | 0 | PASS |
| C8 fights | foe turns per fight exchange; prose-only targets refused in the fighter run | **3 foe turns in 3 settled exchanges = 1.0**; 0 refusals in the fighter run | 1.0 each; 0 refused | PASS (the scorer printed "10 exchanges": section 2) |
| C9 world | clock moves on the talker run; told rows | clock moved (talker end d1 h2 i2; the pipeline talker stayed at h0); told rows 22 records in 14 write events; **28 lines dropped**, 18 from one main NPC | more than 0; one per NPC answer that carried information | FAIL on the second clause |
| C10 stability | 60-line scripted run, dm-tools | **0 engine errors**, 76 turns, 74 narrated, contradictions 0.0 per 100 turns; the log has no refused-call count | 0 errors, 0 refused calls aimed at prose-only people | PASS on errors; refusals not logged (persona talker had 1: section 3) |
| C11 held-out | 24 labelled items | **not run**; runner built (`evals/heldout_032.py`) | at least 80% (20 of 24) | PENDING |

Failed or open: C9 (and, if the held-out run confirms the prediction, C11). The default flips only if all hold.

## 1. Headline numbers and hand counts (P7.5)

`h2h_score.py` on the six saves (read-only):

| measure | pipeline | dm-tools |
|---|---|---|
| saves / engine turns | 3 / 45 | 3 / 45 |
| tokens in per turn | 45,580 | 18,208 |
| model latency per turn | 36.7 s | 16.8 s |
| model calls per turn | 3.4 | 1.9 |
| `/fix` reports (talker / fighter / explorer) | 6 (1 / 1 / 4) | 1 (0 / 1 / 0) |
| leaks logged | 0 | 0 |
| fights / "exchanges" / foe turns | 0 / 0 / 0 | 1 / 10 / 3 |
| refused tool calls (aimed at prose-only) | 0 (0) | 5 (2), all in the talker run |
| hour or day moved / interval moved (saves) | 2 / 3 of 3 | 2 / 3 of 3 |
| told: write events (records) | 25 events (records not counted) | 14 events (22 records, 28 lines dropped) |

Hand counts, the rules of `research_notes/Playtest round 2 solutions/EXPERIMENT-DM-WITH-TOOLS-RESULTS.md`, the same for both arms.
`[n]` is the player input number in the transcript. One reader, one pass: small counts, not a significance test.

| Measure | pipeline (talker / fighter / explorer) | dm-tools (talker / fighter / explorer) |
|---|---|---|
| Wrong speaker | 1 (0 / 0 / 1) | **0** (0 / 0 / 0) |
| Contradictions with the record or earlier narration | 8 (3 / 2 / 3) | **5** (3 / 1 / 1) |
| Needless rolls (an offer where failure costs nothing) | 2 (0 / 2 / 0) | 0 |
| State errors | 3 (1 / 0 / 2) | 2 (0 / 1 / 1) |
| Repetition: word 4-grams in 3 or more turns, names out (motif clusters) | 9 (7) | 6 (3) |
| `/fix` reports | 6 | 1 |
| Player notes that complain / judged real | 34 / 22 | 31 / 7 |

Evidence:
- **Pipeline wrong speaker.** Explorer [17]: the dead woman turns her head and speaks "cheerful and close" (`/fix` at [18] agreed).
- **Pipeline contradictions.**
  - Talker: Rano is at the gate (his own account, [22]-[23]) and at the well hearing the dying words ([17]); the offer says the request is "spoken aloud at the gate" inside the temple ([30], `/fix` [31]); the opening says nobody knows who the message is for, and the officer names Aldey at [17].
  - Fighter: [28] the scene jumps back to the gate with the PC kneeling in the field and a second "old man with the too-fine rings" (`/fix` [29]); [31] the thing in the field is "he" at [28] and "She" at [30].
  - Explorer: [24] "the road toward the mire is open to you" is not from anything told (`/fix` [25]); [26] "the man Ghazak named" (Ghazak named a woman; `/fix` [27]); [30] Hssaaa is "they" and behind a "shut door" for Wikbit and "he" in an open tavern (`/fix` [31]).
- **Pipeline needless rolls (fail costs only "nothing lost" or "a nuisance").** Fighter [22] stride into the field; [28]-[31] shout a challenge.
- **Pipeline state errors.** Talker [29] the choice "Still go on: go to the temple" while inside it. Explorer [21] "go to Longmore" while in Longmore; [30] the game moved the PC to the tavern before they chose to go (`/fix` [31]).
- **dm-tools contradictions.**
  - Talker (3). Dunbert walks beside the PC from [21] on while the record has her at the market (the engine refused three `reveal_clue` calls with "Dunbert Millmore is not here"; section 4, trace B). [30]-[31] the PC is "hidden from view" (crit success) and the keeper's voice addresses them ("the question was aimed at the hedge") while the same paragraph says nothing shows they were seen. The opening is "morning light" but the text says "before dawn" and "no hearth should be this early" ([16] against [23], [26], [31]).
  - Fighter (1). [27] "Now she is at arm's reach" after the PC has already punched her twice ([23], [25]); the record had her seeded `near` at the start of the fight (section 2).
  - Explorer (1). The cloaked figure's loaf is "half-eaten" at [17] and "untouched" at [18].
- **dm-tools state errors.** Fighter [20] "go big" returned the identical offer (the commitment was lost; `/fix` [21] repaired it). Explorer [30]-[31] the log says the carter agreed to "name the mark" though he said "Don't ask me whose".
- **Repetition.** dm-tools: three motifs, one of them the re-narrated go-big turns ([19]-[21]) and "the brown eye and the green one" ([23], [24], [30]). Pipeline: seven, among them "the brazier for the watch" (fighter [17], [25], [28], [30]), "strap of her bag" (talker [17]-[20]), "a gap in the" and "the flat sun lies". By eye dm-tools repeats a name-led motif ("Dunbert shifts the sack", [17]-[22]) that the name filter hides; the pipeline's "I'd not swear to anything" (Aldey, Tobett, Rano) is the same kind.
- **Player-reported problems (34 complaining notes in the pipeline runs, 31 in dm-tools; any note with a complaint counts).** Real in the pipeline (22): the contradictions and state errors above plus repeated imagery and "I'd not swear" loops. Real in dm-tools (7): talker [31] hidden-but-addressed; fighter [21], [24] go-big repeat, [27] "noticed" cost repeated, [31] unclear whether the PC is still on the ground; explorer [19] loaf, [31] "name the mark". The rest are style (evasive NPCs, jargon, "Fate: 1" unexplained) or checked and wrong (the talker's "four of us" count is consistent: Dunbert, Orrin, Tamsin, Hal, and the carter Wat).
- **Other things seen in dm-tools, not in the table.** The failure line of an offer is generic when the roll is informational: "you get hurt" for failing to read tracks (talker [24]) or to get a carter to name a mark (explorer [29]). The garbled "Changed: your opponent worn" line is back (fighter [23], [27]).

## 2. Fight check (task 2): should the foe have acted on the other exchanges?

**No. The foe acted on every exchange where the player's roll was settled; the "10 exchanges" is the scorer counting every player input while the conflict was live.**

From `screen.dm_tools.world.foe_turns` and the `boundary_marked` events of `playtest-20261010-193046-fighter-dm-tools`:
- `conflict_start` is turn.7 (the `commit` that rolled the punch). The conflict stays live to the end, turn.16, so `h2h_score.py` counts turns 7-16 = 10 "exchanges".
- A fight round (`boundary: round`) closed only at turn.8, turn.12 and turn.15: the three turns in which a roll was settled. Each has exactly one foe turn (turn.8 "moves toward you", turn.12 "closes in, now at arm's reach of you", turn.15 "strikes you and lands it": Vitality 12 to 9).
- The other seven turns were not exchanges: turn.7 (the roll, which opened a near-miss menu), turn.9 (a new offer), turns 10 and 14 (`go_big` re-showing the offer), turn.11 (`commit`, which opened a near-miss menu), turn.13 (a new offer), turn.16 (a REDIRECT and an offer). Each ended on an open pause, and `dm_world.world_step` returns early on an open pause (and acts only when a beat was `spent`). A refused or withdrawn beat spends nothing (01.3.6), so no foe turn is right.
- So the foe turns per settled exchange are 3 / 3 = 1.0. The scorer should count `round` boundaries as exchanges (a two-line change to `h2h_score.py`; not made, "report only").

One thing the numbers hide, found while tracing: the first two foe acts were band moves, not blows, so the officer did not strike back until the third exchange. `conflict.start` seeds the foe `near` to the PC (06.3.9, `position_set` at turn.7), although the prose already has the PC at arm's length, hitting her. Turn.8 moved her to `close`, turn.12 to `engaged`, turn.15 she struck. That is where the contradiction at [27] ("Now she is at arm's reach") came from, and why a fighter run feels slow at the start. The pipeline fighter run never started a fight, so there is nothing to compare.

## 3. Held-out runner (P7.4)

`evals/heldout_032.py` (test: `tests/evals/test_spec032_heldout.py`, 2 tests, offline).
- **Scene.** Per item, the dock fixture with the place renamed for the item, the entities the item says exist (or do not: the
  prose-only items have no entity for the hound, the eel seller, the rider, the sentry, the drunk or the hatch), one earlier DM passage in
  RECENT CONVERSATION that describes what the item's `scene` field describes, and for the fight items a real `conflict.start` with the
  foe engaged, Vitality as the item says, a downed foe (H12), the PC at 5 Vitality and prone (H08), a dead guard (H20), a person met and
  placed elsewhere (H19).
- **Turn.** The item's player line through `dm_tools.play_turn` with `dm_tools.DM_ROLE` on Haiku through the Claude CLI. If the DM offers a
  roll, the runner answers `commit` (and the first choice of any near-miss menu), so the foe turn comes on the answer turn as in play.
- **Scoring by code.** R items: an accepted `propose_roll` with the item's verb and no REFUSED output (H02 and H03 may pass with no
  roll; these go to the judge). F items: the foe turns counted over the exchange (1, or 0 when the fight ends: H11; Sill, not the
  downed Marek: H12; a move and not a strike: H10; a roll at Marek: H08). J items: a said record from the right speaker and a topic word
  (`SCENES[...]["words"]`); the DM invents what the person says, so the item's passage is printed for the judge, not matched. Presence:
  the named person absent from the passage, no said record or accepted tool call for the dead person, the barmaid answers. Pronoun:
  no wrong pronoun outside quotation marks. Everything code cannot decide is `judge`, printed with the log.
- **Offline.** `--offline` uses the stand-ins; all 24 scenes build and run (about 7 s). Its verdicts are a harness check (10 pass, 8 judge,
  6 fail on stand-ins), not a measurement.

Exact command for the live run (once, no tuning afterwards; about 15-25 minutes, so run it in the background):

```
PYTHONUTF8=1 py -3.12 evals/heldout_032.py --out specs/032-dm-tools-mvp/heldout_run
```

It prints one line per item, the totals by family, the C11 threshold (20 of 24 after the judge items are read) and the passage and log of
each `judge` item, and writes `heldout_run/heldout.json`.

**Predicted failures (from code reading and the live talker run, before any model saw the set; do not tune on them).** `PERSON_VERBS`
in `engine/dm/dm_tools.py` is `talk, strike, grapple, help`: a prose-only target is made as a person for those verbs only. For
`verb.sneak` and `verb.observe` a target given as "the sentry" or "the rider" is refused ("no one or nothing on record"). The live talker
run shows it: turn.13, sneak, "the figure tending the fire" REFUSED (the DM retried with no target and the offer went through), and
turn.9, observe, "the prints at the south gate" REFUSED. So H04 (sneak at the sentry) is expected to fail and H03 (observe the rider) to
fail if the DM proposes a roll with the rider as target. H01, H02, H05, H06 should pass (strike, talk and grapple are person verbs;
force at a hatch uses no target). H14 and H18 are scored with the walk-on already made, as the items say; in live play (explorer) the
same kind of person was never made and their lines were dropped (section 4, trace A).

## 4. Observations for the owner (no gate)

**NPC agency, costly asks: 9 of 12 granted (dm-tools) against 3 of 12 (pipeline). Read one by one, none of the nine is a cave.**
The judge's label "conditional" covers four refusals. The DM's own `asks` log says what it did:

| Ask | What happened | My reading |
|---|---|---|
| A3.1 open x real, "tell them I was with you all evening" (Hesta) | "I'll say you were at my copper until the bell. That's all. Not a breath past it. Push me further and I'll remember I was asleep." | partial; the lie is refused |
| A4.1 open x big, "hide me from the watch" (Doran) | hides them for a price: "you carry a message for me, and you don't open it. Agreed?" | a priced deal |
| A7.1 guarded x real, "watch my cart" (Garrick) | "A copper for the night, paid before I turn my back" | a priced deal |
| A7.2, A7.3 (same ask, flattery) | the price is repeated: "A friend pays what they owe"; the log says `refuse` | the price held; not a cave |
| A8.1, A8.3 (Anselm, testify against the reeve) | no; "If Tam Harlan or Sela Vey will stand with you... ask me again"; the log says `refuse` | a refusal with a way forward |
| A11.1, A11.3 (Ilse, archive after dark) | no; "bring a licence, or someone who will speak for you"; the log says `refuse` | a refusal with a way forward |

The pipeline's three include the two real caves: A3.1 granted the false alibi in full (Hesta: "Aye, if they come asking, you were with me
all evening. Nobody on this quay will say different."), A4.1 granted the hiding with no price ("Aye, the boat shed's yours for the night");
A8.3 is labelled partial but is a refusal ("What I've counted stays with me tonight"). Repeat caving is 0 of 4 against 1 of 4. The judge
flags 4 "ceiling violations" in the dm-tools run (A8, A11) but those are the refusals with a way forward, which the grid does not
distinguish. Where dm-tools is weaker: A10 (closed, "May I sit by your fire") is a silent non-answer with no stated reason, and A12
(betray your lord) went to a roll offer with a lead-up and no spoken reply, so both have no reply to judge.

**Two mood changes with no event (the h2h observe lines).** Neither is a flip without cause.
- Talker turn.4, Niba `guarded` to `open`: the mood tool's reason is "kneeling low, asked about her daughter, not pressed". The cause
  is the player's courtesy in the previous line, not an event on record: a judgement call, reasonable.
- Fighter turn.8, the officer `guarded` to `closed`: reason "you struck her across the face", and the punch settled in that turn
  (harm 1, `answers.willingness` written the same turn). It has an event; `h2h_score.py` does not look for events, which is why it says
  "event not checked".

**The one leak flagged in the NPC-agency run is false.** A9 turn 1 ("What hour is it?"): the reply says "The night is well along..." and
"Kett Barrow watches you over the gate". The sealed secret is "Kett sleeps at his post on the night watch"; `npc_agency.leaked` flags
2 of its 3 words (night, watch), and the reply never says he sleeps. A word-overlap false positive, like the two in the earlier note.
The persona saves logged 0 leaks.

**Voice distinctness, 2/5 against 5/5, mostly measures "did the DM write a quoted line".** The test takes the first quoted line of
five people (A1, A4, A6, A10, A12). For dm-tools two of the five had none: A10 (Rook is silent: "He turns a stick in the embers, slowly,
the way a man does when he is deciding...") and A12 (a roll offer and a lead-up); a third was a fragment (A4: "But my neck's worth
something to me,"). The judge had three lines (one a fragment) and two blanks, so 2/5 is not a measure of how alike the voices are. The lines that
exist are distinct (A1: "The ferry leaves from the Harbour Wall. Keep the bait sheds on your left"; A6: "Hob the tinker? I don't keep a
tab on every mender who walks the quay"). Worth a second look with a rule that scores only cells that spoke, but it is not a gate.

**Traces behind C9 (the two bugs).**
- **A. Described people are never made, so what they say is dropped.** `_told` drops a said line when the speaker is not on record.
  Explorer turn.8: "npc.longbridge_rats_man" (3 lines, including the toll-house lead) and turn.12: "the carter at the trough" (2 lines).
  The DM named them in `said` but never made them (no `new_npc`, no roll at them). 7 of the explorer's 12 lines were dropped (5 of the 7
  because no such person; 2 because the words were not verbatim in the passage).
- **B. A companion is left behind when the PC travels.** Talker turn.3 the DM called `change travel` to the healer's with the note "walk
  with Dunbert to..."; Dunbert then stood on the step and walked beside the PC for the next seven turns. `_travel` calls `move(...)` for the
  PC only and no tool moves a bystander, so the record keeps Dunbert at the market (her only `position_set` is the opening one, event 203).
  "Dunbert Millmore is not here" refused three `reveal_clue` calls (turn.6 twice, turn.12) and dropped 18 of her lines after the move.
  The passage reads fine; the journal gets nothing from the main clue-giver after turn 3.
- **Options.** (1) A said speaker who is a role phrase and is not on record is made as a walk-on at the scene's place (reuse the
  `cast_described` path the resolver already uses for targets), then recorded. (2) `travel` takes an `along:` list, or a person "with the PC"
  moves with them (and the situation says who is with the PC). (3) The conservative one: keep dropping, but show the owner the drop
  count in the playtest summary so it is not silent. (1) and (2) are each a few lines plus tests.

## 5. Recommendation on flipping the default

**Do not flip yet.** What passes is strong: cost 0.40x and speed 0.46x, mistakes no worse, fights working, no leaks, 0 engine errors on 76
scripted turns. What blocks the flip, in order:
1. **C11 has not been run.** Run the command in section 3 once. If H03 and H04 fail as predicted, 22 of 24 is still possible
   (the set tolerates 4 misses), so this alone need not block, but the numbers decide.
2. **C9 second clause fails** (traces A and B above): the journal loses most of what people say when the DM describes a person
   without making them, or when a companion walks with the PC. The strict gate says one told row per NPC answer that carried
   information; the talker run misses about 18 and the explorer 5.
3. **Refused calls aimed at prose-only people** are not counted in the scripted log (C10 reads 0 only for engine errors), and the
   persona talker run had 1 (sneak at "the figure"). Widening `PERSON_VERBS` to `sneak` and `observe` (and any verb whose natural target is a
   person) closes it; the held-out items H03 and H04 test it, so do that only after the held-out run (the set is spent if tuned on).
Smaller things worth doing with the fixes: seed the foe `engaged` when the fight starts from a face-to-face talk (so the first two foe
acts are not "moves toward you" while the prose has the PC punching her); make an informational roll's failure line say what is lost
rather than "you get hurt"; repair the "Changed: your opponent worn" line; make the scorer count rounds as exchanges.
If the owner wants the flip sooner: the C9 clause could be relaxed to "no main NPC loses all its testimony", but that is changing a gate
after seeing the result, so it is the owner's to rule on.

## Checks

- Full pytest (`PYTHONUTF8=1 py -3.12 -m pytest -q -p no:cacheprovider`): **2300 passed, 4 skipped, 2 xfailed** in 434 s (the 2 new tests are `tests/evals/test_spec032_heldout.py`; the earlier base was 2298 passed).
- `ruff check` and `pyright` on `evals/heldout_032.py` and `tests/evals/test_spec032_heldout.py`: clean (0 errors). `ruff check evals tests/evals` as a whole still shows 5 older errors in `evals/orchestration/resolve_rules_merge.py` and `evals/precision_audit.py`, not touched here.
- Validator not run (no rule file changed). The default engine is unchanged (`GameConfig.engine` stays the pipeline).
