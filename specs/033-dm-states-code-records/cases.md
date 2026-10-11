# Cases 033: made-up and edge cases, enumerated from the data

Each row is a test (offline, ScriptedModel unless marked). "REFUSED" means the tool returns the refusal with the legal
options listed (one revision, then dropped and logged). Every game in `tests/guard/games_033.py` replays these under
the VIII.9 guard. Data read at 8a8bcb8: 15 verbs (`basic_verbs.yaml`), 13 change kinds, 9 costs, 4 default behavior
lists, the 01.13.7 footing rows.

## C1. Every verb x the new `propose_roll` fields

`kinds` = today's derived target kinds; R makes them the data field `target_kinds`. `as` default = they when kinds is
person only, else thing. Fallback costs = `verb_costs` minus those needing `fail_on` (exposure and gear unless a
listening clock / `fail_on`; closed_door unless the target is a person on record).

| Verb | kinds | `approach` options (besides plain) | `force` | reach check | fallback costs |
|---|---|---|---|---|---|
| move | object, person | flying or teleporting | ignored | none | none listed: first source's first cost |
| observe | object, person | reading an unknown script; magical sight | ignored | none | time, drain |
| recall | none | specialist lore | ignored | none | time, drain |
| talk | person | speaking a language not held | ignored | none | closed_door (target on record), time |
| strike | person, object | weapon techniques | ignored | engaged if a band is recorded | harm, footing |
| grapple | person | (none) | ignored | engaged if a band is recorded | harm, footing |
| force | person, object | picking a lock | REQUIRED | engaged if a band is recorded and the target is a creature | harm, footing |
| exert | object | (none) | ignored | none | harm, footing, drain |
| evade | none | (none) | ignored | none | first source's first cost |
| sneak | person | disguise as a specific person | ignored | none | time |
| handle | object, person | surgery; smithing and fine crafts; lockpicking; mounted combat | ignored | none | first source's first cost |
| endure | object | (none) | ignored | none | first source's first cost |
| setup | person, object | (none) | ignored | none | first source's first cost |
| help | person | (none) | ignored | none | first source's first cost |
| ready | none | reactions beyond ch.06's | ignored | none | first source's first cost |

Per verb, one test each for:
- C1.a `target` an id; `target` words with each `as` (5 values) and with no `as` (the default above). Only a
  person or creature makes an entity, and `t.made` names it. A thing never refuses.
- C1.b `approach` = each listed entry: with a `covered_by` licence held, G2; without, G3 redirect listing
  its `covered_by` licences. An `approach` from another verb's list is accepted (00.12.3 reads every verb's exclusions). An
  unknown string is REFUSED with the list.
- C1.c `reads` true on observe, handle, talk: target with words on record and a readable tongue, no roll
  ("plain reading"); literacy on record without letters, G3; an unreadable tongue, refused by `cannot_read`. `reads`
  false with a target bearing writing: the normal verb path (no word test promotes it).
- C1.d `change_kind=move_to`, `change_what` each band (5) x mover actor/target: success writes that band both ways;
  failure writes none; success at a cost writes it; a place id in `change_what` is REFUSED ("use travel or change
  position").
- C1.e `weapon`: a held item id (weight from its tags); `unarmed`; an id the actor does not hold (REFUSED); omitted
  with a `wields` fact (that item); omitted without (unarmed). Only strike reads it; other verbs ignore it.
- C1.f `nonlethal` true on strike, grapple, force: harm mode nonlethal; the method text is unchanged (no
  "(nonlethal)" appended).
- C1.g `change_kind=restrain` on grapple: the ladder at reach 1-4 (grabbed S1, grabbed S2, restrained, pinned);
  grapple with change_kind none or take: no hold. `change_kind=free` with the actor held: the hold ends on success.

## C2. Force (06.5.3)

| force | reach 1 | reach 2 | reach 3 | reach 4 |
|---|---|---|---|---|
| push | target off balance | pushed one band (link breaks) | pushed two bands | as 3 (+ follow-up lever) |
| prone | target off balance | `cond.prone`, band unchanged | prone and off balance | as 3 |
Plus: force omitted (REFUSED); a target with no recorded band (no band check; a push writes from engaged); an object
target (no band, no condition; `change_kind` decides, e.g. open).

## C3. Positions without a roll (`change position`)

PC to each band vs an NPC here; NPC to each band vs the PC; NPC to a place id (moves them); PC to another place
(REFUSED: use travel); `what` missing for a band (REFUSED); `who` dead or gone (REFUSED). A Strike after
`change position to=engaged` is not refused; before it, at a recorded `near`, REFUSED "not in reach".

## C4. Foe acts (06.9.4 option set) x foe state

Legal acts per state (code lists them in the FIGHT block; an illegal pick lapses with its reason):

| Foe state | strike | close_in | withdraw | stand | break_free | grapple | flee | yield | wait |
|---|---|---|---|---|---|---|---|---|---|
| engaged, free | yes | no | yes | no | no | yes | yes | yes | yes |
| close/near/far, free | no | yes | no | no | no | no | yes | yes | yes |
| prone | no | no | no | yes | no | no | no | yes | yes |
| grabbed by the PC | yes | no | no | no | yes | yes | no | yes | yes |
| restrained by the PC | yes (close-quarters only; ponytail: any weapon, logged) | no | no | no | yes | no | no | yes | yes |
| pinned by the PC | no | no | no | no | yes | no | no | yes | yes |
| down, dead or fled | (not listed; not asked) | | | | | | | | |

Tests: each legal cell rolls the stated dice (seeded) and writes the stated result: strike hit/miss/critical with harm
by `_line` and lethal by `effective`; `nonlethal` true; grapple success (grabbed S2) and critical (restrained);
break_free success, failure, critical (holder off balance); flee (band distant, leaves the scene, fight ends when no
foe is able); yield (`defeated` yielded, fight ends). Each illegal cell lapses with the reason in WHAT THE WORLD DID.
Plus: `target` a companion; `target` absent or dead (lapses); two foes, one omitted (one re-ask, then it waits,
logged); foes given with a paused `propose_roll` (stored, run on the answer); the PC's result downs the foe (its act
lapses); an IDLE exchange (refused, question, withdrawn: no foe acts); `foes` given with no fight (ignored, logged).

## C5. Costs x `fail_on` and form

| Cost | needs | `fail_on` | form | fallback eligible |
|---|---|---|---|---|
| cost.harm | none | ignored | | yes |
| cost.drain | a quantity the actor has | ignored | | yes (refused at landing if empty, 01.9.4) |
| cost.time | a listening clock, else the mode's time row | ignored | | yes |
| cost.exposure | an observer or a listening clock | the observer id | | only with a listening clock |
| cost.gear | an item | the item id (must be held by the actor) | severity row | no |
| cost.footing | (opponent for grabbed/controlled) | ignored | picked after the roll | yes |
| cost.closed_door | a person or obstacle | the person id (else the target) | | when the target is a person on record |
| cost.shortfall | success at a cost | ignored | | alternate only |
| cost.twist | rolls `tbl.twist` | ignored | | last resort (01.13.1 d) |

Footing options offered on COST TO SHAPE, per severity (only those that can land):

| Sev | options | can land when |
|---|---|---|
| S1 | `off_balance`; `lose:flag.in_cover` / `flag.elevated` / `flag.hidden` | always; the flag is held |
| S2 | `prone`; `grabbed` (by the opponent); `band_back` (one band against the intent); `slide:<place id>` | always; an engaged opponent; a band is recorded; an adjacent exit |
| S3 | `restrained`; `cornered`; `slowed`; `separated` (two bands from allies or goal) | always; always; always; a band is recorded |
| S4 | `pinned`; `lower:<place id>`; `controlled` (restrained by the opponent) | always; an exit marked lower/worse; an opponent |
| S5 | `trapped` (restrained until cleansed); `swept:<place id>` | always; a distant place on record |
Tests: every option at its severity; `cost_form` naming an option not offered (REFUSED in the re-ask, then nothing
written); `cost_form` omitted (one re-ask joined with missing foes, then nothing written, logged); exposure with
`fail_on` absent and no clock (REFUSED at propose); gear with an item the PC does not hold (REFUSED); closed_door
`fail_on` a different person than the target (that person's standing drops).
Reversal (01.9.3, `reverses_goal` table): persuade_to/learn with closed_door on the same person is never paid on a
success at a cost; other kinds have no reversing ids (the old word patterns are not consulted).

## C6. Leads (12.8.1, PR-12-3)

Due with open threads and sources (the DM is told both; nothing spawned; trigger lowered, streak reset); due with no
threads ("no open thread is on record"); due while a roll is offered (told after it resolves); the DM ignores it (no
state change; the streak counts again); the DM brings one in with `new_npc` (an ordinary walk-on).

## C7. Witnesses (15.9.4)

A necessary node below its live placements at a scene end: WITNESS NEEDED once with the node id; told again only after
a new shortfall; the DM's `new_npc knows=<node id>` places the reserve on that walk-on and a later `reveal_clue` to
them delivers it; `new_item knows=<node id>` (a document); `knows` an unknown or already-found node (REFUSED); the DM
ignores it (nothing placed, the node stays short); no haven on record (still told; nothing auto-placed).

## C8. Walk-ons and identity

`as` x entry point: propose_roll `target`, `said.npc`, `change who` (coin, give_item, condition, npc_leaves, fight),
`reveal_clue npc`, `mood npc`, `new_npc`: he, she, they (person, pronouns as given, a rolled name); creature (`mind:
animal`, "it", no rolled person); thing (no entity; refused only in a person-only slot). Plus: exact recorded name
("Edda Brightcote") resolves; a partial name ("Edda") does not (it becomes a new walk-on: the DM must use the id);
a sealed entity's exact name does not resolve; two entities with the same name (ambiguous: words, made new); `"pc"`
is the PC; "you" and "the player" are words (a person-only slot makes a walk-on named so; logged in P7);
`new_npc name="Hal"` gives that name; the same words twice in one turn are one walk-on (`t.aliases`).

## C9. Testimony

Kept as given: a present living speaker; a line repeated from earlier; a line whose words are not in the passage; a
line that overlaps a clue the DM delivered. Dropped (logged): a dead, gone or absent speaker. Unknown words with and
without `as`: a walk-on is made, then the line is kept.

## C10. Retire (11.13.1)

`/retire` (exact) opens the confirmation; `/retire` with a roll offered (withdrawn first, as any new message);
"I retire." goes to the DM; the DM's `end_game` opens the confirmation; `keep_playing` closes it; the ending menu
answered by id and by number; free text at the menu shows it again. Pipeline games keep today's behavior.

## C11. Measures (evals, offline stand-ins)

The judge stand-in labels a fixture; the report prints each count with "precision unmeasured" under 20 hand verdicts
and with p and n at 20 or more; a priced deal is labelled `priced`, not a cave; the engine writes no `leaks` or
`log_only` stats.

## C12. The guard itself

A planted call to each denylisted function from a dm-tools tool fails the runtime test with "constitution VIII.9" and
the inventory id; `conflict.start` from `_fight` passes and from `_roll` fails; a planted `re.search` in `dm_tools.py`
fails the static test; the same line allow-listed as P passes; `VIII9_GUARD=log` writes hits to JSONL and does not
raise.
